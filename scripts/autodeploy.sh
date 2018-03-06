#!/bin/bash
##############################################################################################################
# Auteur    : Mickael A. CABREIRO
# Date      : Mach 4th 2018	 
# OS Testes : Raspian OS
# Version   : 1.1
#-------------------------------------------------------------------------------------------------------------
# DESCRIPTION
#     This script is intended to be used to autodeploy the AlgoCrypto projec (Cyril SACENDA) 
#     This script provide the following actions:
#	1. deploy python backend scripts from github
#
# SYNTAX
#     (1) Display usage screen
#           autodeploy.sh -h
#
#     (2) Display script version
#           autodeploy.sh -V
#
# OPTIONS
#     -h
#        display the script usage
#
#     -V
#        display the script version
#
# RETURN CODES
#     0 : All initiated deployments finished successfully
#     1 : warning occurred
#     2 : XXXX deployment failed
#=============================================================================================================
#=============================================================================================================
# MODIFICATIONS
#-------------------------------------------------------------------------------------------------------------
#	Version 1.1 : Adding Cron management
##############################################################################################################

#	Parameters 
# ---------------------------------

# Constants
# ---------
	readonly __PROG_VERS="1.1"
	readonly __DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
	readonly __PROG="${__DIR}/$(basename "${BASH_SOURCE[0]}")"
	readonly __BASE="$(basename ${__PROG} .sh)"

# Retun Codes
	readonly SUCCESS=0
	readonly WARNING=1
	readonly ERROR=2

# Error reporting
	readonly DATE=`date +%Y%m%d`
	readonly LOGFILE="autoDeploy_${DATE}.log" 
#exec 3>&1 1>>${LOGFILE} 2>&1

# Options activations
__DEPLOY_FRONT=0
__DEPLOY_BACK=0
__DEPLOY_CRON=0

# GIT Parameters
# --------------
__Git_Front=""
__Git_Back=""

__DB_HOST="algocryptos.c592sqstvfao.eu-west-3.rds.amazonaws.com"
__DB_USER="algocryptouser"

# Cron Parameters
# ---------------
NewCron="${__AppRootDir}/algocryptos_scripts/script/script.txt"

# Functions
# ---------

# -------------------------------------------------------------------------
#   Function : usage
# -------------------------------------------------------------------------
# ARGUMENTS
#     None
# RETURNS
#     None
# -------------------------------------------------------------------------
usage()
{
cat << __CAT_EOF__
=================================================
${__BASE}
=================================================
DESCRIPTION
	This script is intended to be used to autodeploy the AlgoCrypto projec (Cyril SACENDA) 
	This script provide the following actions:
		1. deploy python backend scripts from github

SYNTAX
     (1) Display usage screen
           autodeploy.sh -h

     (2) Display script version
           autodeploy.sh -V
     
     (3) Autodeploy 

OPTIONS
     -a
	Update all components of algocrypto app (default option)

     -b
	Update backend component

     -c
	Update crontab 

     -f
	Update frontend component

     -h
        display the script usage

     -V
        display the script version

RETURN CODES
     0 : All initiated deployments finished successfully
     1 : warning occurred

__CAT_EOF__
}



# -------------------------------------------------------------------------
#   Function : showVersion
# -------------------------------------------------------------------------
# ARGUMENTS
#     None
# RETURNS
#     None
# -------------------------------------------------------------------------
showVersion()
{
cat << __CAT_EOF__
${__BASE} :
	version : ${__PROG_VERS}

__CAT_EOF__

return ${SUCCESS}
}

# -------------------------------------------------------------------------
#   Function : StopCron
# -------------------------------------------------------------------------
# ARGUMENTS
#     None
# RETURNS
#     None
# -------------------------------------------------------------------------
stopCron()
{
	crontab -l > /tmp/crontab_bkp${DATE}
	touch /tmp/emptyfile
	if [ -f /tmp/emptyfile ]
	then
		crontab /tmp/emptyfile
		rm /tmp/emptyfile
	else
		echo "${__BASE} : ERROR : Crontab stop : Empty file not generated!"
	fi
}

# -------------------------------------------------------------------------
#   Function : releaseCron
# -------------------------------------------------------------------------
# ARGUMENTS
#     $1 - [OPTIONAL] File use to update crontab - [DEFAULT] /tmp/tempfile
# RETURNS
#     None
# -------------------------------------------------------------------------
releaseCron()
{
	local Filetoload="/tmp/crontab_bkp${DATE}"

	echo "${__BASE} : DEBUG : deploy Cron #ARGS = $#"
	# If a new file is provide using function parameter = means update
	[ -n $1 ] && Filetoload="$1"
	echo "${__BASE} : DEBUG : Filetoload=$1"
	
	echo "${__BASE} : INFO : Updating crontab unsng file ${Filetoload} ... ..."
	
	if [ -r $Filetoload ]
	then
		$(crontab ${Filetoload})
	else
		echo "${__BASE} : ERROR : Update crontab - Unable to find source cron file:"
		echo "${__BASE} : ERROR : '--> $Filetoload"
		exit ${ERROR}
	fi

	echo "${__BASE} : SUCCESS : Crontab updated successfully."

}

# -------------------------------------------------------------------------
#   Function : DeployBackend
# -------------------------------------------------------------------------
# ARGUMENTS
#	None
# RETURNS
#     None
# -------------------------------------------------------------------------
DeployBackend()
{
	set -xv
	local AppBuilDir=""
	# Stop Cron - Avoid unforseen interaction
	# ---------------------------------------
	stopCron	

	echo "${__BASE} : DEBUG : ${__AppRootDir} "
	if [ -n $__AppRootDir ] 
	then
		AppBuilDir="${__AppRootDir}/algocryptos_scripts"
		if [ ! -d "${AppBuilDir}" ] && [ ! -d "${AppBuilDir}/.git" ]
		then
			echo "${__BASE} : ERROR : ${AppBuilDir} does not exist or is not a git local repository!"
			echo "${__BASE} : ERROR : Please check you app root directory or initialise the git by:"
			echo "${__BASE} : ERROR : '--> git clone <git repository>"
			exit ${ERROR}
		fi
	else
		echo "${__BASE} : ERROR : App Root Directory issue!"
		exit ${ERROR}
	fi

	#Retrieve Git
	cd "${AppBuilDir}"
	git checkout .
	git pull origin master
	echo "${__BASE} : INFORMATION : DEPLOIEMENT DU BAKEND $(pwd)" 
	
	# Change DB config
	# ----------------
	# sed -i -e '/^this/ s/test/something/'
	if [ -s "${AppBuilDir}/commons/config/config.ini" ]
	then
		$(sed -i -e "/^dbhost/ s/localhost/${__DB_HOST}/" "${AppBuilDir}/commons/config/config.ini")
	fi
	# Adjust Database with new tables
	# -------------------------------
	if [ -s "${AppBuilDir}/db/modifsBDD.sql" ]
	then
		# Parse file and substitute user postgre by Prod User
		$(sed -i -e "s/postgres/$__DB_USER/g" "${AppBuilDir}/db/modifsBDD.sql")
		#$(psql -h ${__DB_HOST} -d algocryptos -U $__DB_USER -a -f "${AppBuilDir}/db/modifsBDD.sql")
	else
		echo "${__BASE} : WARNING : File ${AppBuilDir}/db/modifsBDD.sql not found" 
		echo "${__BASE} : WARNING : Skipping database adjustments..."
	fi

	# Reprise de la crontab (si option de mise à jour non activée)
	# -------------------------------------------------------------
	[ $__DEPLOY_CRON -eq 1 ] && releaseCron
	set +xv
}

# -------------------------------------------------------------------------
#   Function : DeployFront
# -------------------------------------------------------------------------
# ARGUMENTS
#	None
# RETURNS
#     None
# -------------------------------------------------------------------------
DeployFront()
{
	# Function Local Parameter :
	# --------------------------
	local ToPushDir=""
	local S3Bucket=""
	local AppBuilDir=""

	# Retrieve Github

	# Stopping NodeJS
	pm2 stop www

	#Checking if 3 agurments are passed to function
	echo "$__BASE : DEBUG : $#"
	echo "$__BASE : DEBUG : $__AppRootDir"
	# We validate that a RootDirectory is set
	if [ -n $__AppRootDir ] 
	then
		AppBuilDir="${__AppRootDir}/algocrypto_web/build"
		if [ -n $2 ]
		then
			ToPushDir="${2}"
		else
			ToPushDir="./front"
		fi

		if [ -n $3 ]
		then
			S3Bucket="${3}"
		else
			S3Bucket="s3://algocrypto"
		fi
		aws s3 sync ${ToPushDir} ${S3Bucket} 
	else 

		echo "$__BASE : ERROR : AWS Sync Not possible !!!"
		echo "$__BASE : ERROR : App working directory set to ${__AppRootDir}"
		exit ${__ERROR}
	fi

	# starting NodeJs
	pm2 start www
	return ${SUCCESS}
}
######################################################################################################
#
# MAIN - Script execution really Starts here
#
##########################################################################################

echo "OPTIND : ${OPTIND}"
# Parameters parsing
# ------------------
while getopts ":abcfhV" option
do
	# Without options it will do a full deployment unless, we reset to have a only on action
echo "OPTIND : in the getopts :  ${OPTIND}"
	if [ $OPTIND -eq 2 ] 
	then
		__DEPLOY_FRONT=1
		__DEPLOY_BACK=1
		__DEPLOY_CRON=1
		echo "$__BASE : DEBUG : The first debug infra!"
	fi


	echo "$__BASE : DEBUG : IN THE GETOPTS"
	case "${option}" in
		a)
			;;		# Deploy all part of AlgoCrypto Application
		b)			# Deploy Only the Back-end
			__DEPLOY_BACK=0
			;;
		c)
			__DEPLOY_CRON=0
			;;
		f)			# Deploy Only the Front-end
			__DEPLOY_FRONT=0
			;;
		h)			# Usage
			usage
			exit ${SUCCESS}
			;;
		V)			# Version
			showVersion || return ${ERROR}
			exit ${SUCCESS}
			;;
        	\?)
			echo "${__BASE}[${LINENO}]: ERROR: Invalid option '-${OPTARG}'."
			exit ${ERROR}
			;;
		:)
			print -u2 "${__BASE}[${LINENO}]: ERROR: Missing mandatory argument for option '-${OPTARG}'."
	 		exit ${ERROR}
			;;
	esac
done
shift $(($OPTIND - 1))

# Working Dir setup & Validation
# ------------------------------------
if [ $# -eq 1 ] && [ -n $1 ] 
then
	if [ -d $1 ]
	then
		# Setting up the AppWorking root Directory - Root directory where subsequent applications have to be deployed
		readonly __AppRootDir="$(cd $1  && pwd)"
		echo "$__BASE : INFORMATION : App working directory set to ${__AppRootDir}"
	else
		echo "$__BASE : ERROR : $1 is not a directory or does not exists"
	fi
else
	echo "$__BASE : ERROR : Missing Mandatory argument working Directory"
	echo "$__BASE : INFO  : '--> autodeploy.sh <App working directory>"
	exit ${ERROR}
fi

echo "$__BASE : DEBUG : __DEPLOY_BACK = ${__DEPLOY_BACK}"
echo "$__BASE : DEBUG : __DEPLOY_CRON = ${__DEPLOY_CRON}"
echo "$__BASE : DEBUG : __DEPLOY_FRONT = ${__DEPLOY_FRONT}"

if [ ${__DEPLOY_BACK} -eq 0 ]
then
	#deploy Backend following the define sequence
	DeployBackend
	echo "$__BASE : DEBUG : DEPLOY BACKEND option active"
fi

if [ ${__DEPLOY_CRON} -eq 0 ]
then
	#deploy Backend following the define sequence
	echo "$__BASE : DEBUG : DEPLOY CRON"
	stopCron	
	NewCron="${__AppRootDir}/algocryptos_scripts/scripts/scripts.txt"
	echo "$__BASE : DEBUG : DEPLOY CRON - NEWCRONFILE = ${NewCron}"
	releaseCron ${NewCron}
fi

if [ ${__DEPLOY_FRONT} -eq 0 ]
then
	echo "$__BASE : DEBUG : DEPLOY FRONT TEST"
# - CMD -	DeployFront dirtest frontdir bucket
fi

echo "Hello World!"
#cat "${__DIR}/Logo.ascii"
