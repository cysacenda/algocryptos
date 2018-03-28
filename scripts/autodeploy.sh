#!/bin/bash
##############################################################################################################
# Auteur    : Mickael A. CABREIRO
# Date      : Mach 4th 2018	 
# OS Testes : Raspian OS
# Version   : 1.4
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
#     -b
#        Deploy backend
#
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
#	Version 1.2 : Changing strategy on PM2 utility. Now, reloading configuration
#	Version 1.3 : Refactoring Zip actions into functions
#	Version 1.4 : Refactoring Git actions into functions
##############################################################################################################

#	Parameters 
# ---------------------------------

# Constants
# ---------
	readonly __PROG_VERS="1.3"
	readonly __DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
	readonly __PROG="${__DIR}/$(basename "${BASH_SOURCE[0]}")"
	readonly __BASE="$(basename ${__PROG} .sh)"

# Retun Codes
	readonly SUCCESS=0
	readonly WARNING=1
	readonly ERROR=2
	__EXIT_STATUS=$ERROR

# Error reporting
	readonly DATE=`date +%Y%m%d`
	readonly DATETIME=`date +'%Y%m%d_%H%M%S'`
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
NewCron=""

# Exit Flags
# ----------
__DB_ADJUSTMENT=1

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
     
     (3) autodeploy all components 
     	   autodeploy.sh [-a] <Application Root Directory>

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
     2: Error occured
__CAT_EOF__
}


# -------------------------------------------------------------------------
#   Function : _TRAP_CTRL_C 
# -------------------------------------------------------------------------
# ARGUMENTS
#     None
# RETURNS
# -------------------------------------------------------------------------
_TRAP_CTRL_C()
{
	tput setaf 1 
	echo "---------------------------------------------------------------------"
	echo " TRAPPED SIGNAL CAUGHT : ctrl+C"
	echo "---------------------------------------------------------------------"
	echo " Application left in inconsistent state "
	
	tput sgr0
	exit $ERROR
}

trap  _TRAP_CTRL_C INT 

# -------------------------------------------------------------------------
#   Function : _TRAP_CTRL_C 
# -------------------------------------------------------------------------
# ARGUMENTS
#     None
# RETURNS
# -------------------------------------------------------------------------
_TRAP_EXIT()
{
	if [ $__EXIT_STATUS -eq $ERROR ]
	then
		tput setaf 1 
		echo " Autodeploy.sh existed anormaly"
        	echo " Please review logs to correct issues !!!!"

		# If Trap occures between DB modifications and cleaning git --> Force cleaning git
		if [[ $__DB_ADJUSTMENT -eq 1  ]]
		then
			echo "-----------------------------------------------------------------------------"		
			echo "Adjusting git due to DB modificationsi on Git before reruning the script	   "
			echo "-----------------------------------------------------------------------------"
		fi

	else
		tput setaf 2 
		echo " Autodeploy.sh existed Successfully!"
        	echo " 	Enjoy AlgoCryptos Tools ! "
	fi

	tput sgr0

	exit $ERROR
}
trap _TRAP_EXIT EXIT

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

	echo "$__BASE [${LINENO}] : INFORMATION : Stopping Crontab!" 
	echo "$__BASE [${LINENO}] : INFORMATION : Generating Backup File : /tmp/crontab_bkp${DATE}" 
	crontab -l > /tmp/crontab_bkp${DATE}
	echo "$__BASE [${LINENO}] : INFORMATION : Generating File /tmp/emptyfile" 
	touch /tmp/emptyfile

	if [ -f /tmp/emptyfile ]
	then
		crontab /tmp/emptyfile
		echo "$__BASE [${LINENO}] : INFORMATION : Crontab purged successfully!"
		echo "$__BASE [${LINENO}] : INFORMATION : Removing empty file"
		rm /tmp/emptyfile
	else
		echo "$__BASE [${LINENO}] : ERROR : Crontab stop : Empty file not generated!"
		exit ${ERROR}
	fi
	echo echo "$__BASE [${LINENO}] : Crontab succefully suspended"
	return ${SUCCESS}
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

	# If a new file is provide using function parameter = means update
	if [ -n $1 ]  && [ $# -eq 1 ] 
	then
		Filetoload="$1"
	fi

	echo "$__BASE [${LINENO}] : INFO : Updating crontab unsing file ${Filetoload} ... ..."
	
	if [ -r $Filetoload ]
	then
		$(crontab ${Filetoload})
	else
		echo "$__BASE [${LINENO}] : ERROR : Update crontab - Unable to find source cron file:"
		echo "$__BASE [${LINENO}] : ERROR : '--> $Filetoload"
		exit ${ERROR}
	fi

	echo "$__BASE [${LINENO}] : SUCCESS : Crontab updated successfully."
	return $SUCCESS
}

# -------------------------------------------------------------------------
#   Function : Gitpull
# -------------------------------------------------------------------------
# ARGUMENTS
#	$1 Directory to sync
# RETURNS
#     None
# -------------------------------------------------------------------------
Gitpull()
{
	local AppBuilDir=""	

	[ $# -eq 1 ] && AppBuilDir="${1}" || echo "$__BASE [${LINENO}] : ERROR : Calling GitPull function using icorrect parameters!"

	if [ -d "${AppBuilDir}" ] && [ -d "${AppBuilDir}/.git" ]
	then
		cd "${AppBuilDir}"
		git checkout .
		git pull origin master
	else
		echo "$__BASE [${LINENO}] : ERROR : ${AppBuilDir} does not exist or is not a git local repository!"
		echo "$__BASE [${LINENO}] : ERROR : Please check you app root directory or initialise the git by:"
		echo "$__BASE [${LINENO}] : ERROR : '--> git clone <git repository>"
		exit ${ERROR}
	fi
	return $SUCESS
}

# -------------------------------------------------------------------------
#   Function : Gitpush
# -------------------------------------------------------------------------
# ARGUMENTS
#	None
# RETURNS
#     None
# -------------------------------------------------------------------------
Gitpush()
{
	if [ $# -eq 1 ] && [ -e $1 ] 
	then
		echo "$__BASE [${LINENO}] : INFORMATION : git add ${1} " 
		git add $1
		echo "$__BASE [${LINENO}] : INFORMATION : commiting" 
		git commit -m "autodeploy.sh : Cleaning SQL modification File ${1}" 

		echo "$__BASE [${LINENO}] : INFORMATION : pushing to github" 
		git push
	else
		echo "$__BASE [${LINENO}] : ERROR : No file to be pushed"
	fi
	# Add file to push
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
	local AppBuilDir=""
	# Stop Cron - Avoid unforseen interaction
	# ---------------------------------------
	stopCron	

	# Retrieve Git Repository
	# -----------------------

	if [ -n $__AppRootDir ] 
	then
		AppBuilDir="${__AppRootDir}/algocryptos_scripts"
		echo "$__BASE [${LINENO}] : INFORMATION : DEPLOIEMENT DU BAKEND $(pwd)" 
		Gitpull $AppBuilDir
	else
		echo "$__BASE [${LINENO}] : ERROR : App Root Directory issue!"
		exit ${ERROR}
	fi
	
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
		$(psql -h ${__DB_HOST} -d algocryptos -U $__DB_USER -a -f "${AppBuilDir}/db/modifsBDD.sql")
		# 
		if [ $? -eq 0 ]
		then
			echo  "$__BASE [${LINENO}] : INFORMATION : Database successfully adjusted! "
			echo "$__BASE [${LINENO}] : INFORMATION : cleaning modifBDD.sql file"
			
			__DB_ADJUSTMENT=1
			# Adjust Git repository to avoid multiple Databases modifications
			echo "" > "${AppBuilDir}/db/modifsBDD.sql"
			Gitpush "${AppBuilDir}/db/modifsBDD.sql"
			[ $? -eq 0 ] && __DB_ADJUSTMENT=0 || echo "$__BASE [${LINENO}] : ERROR : Pushing modifications to Git!"
		else
			echo "$__BASE [${LINENO}] : ERROR : ${AppBuilDir}/db/modifsBDD.sql executed but finish with error!"
			exit $ERROR
		fi 
	else
		echo "$__BASE [${LINENO}] : WARNING : File ${AppBuilDir}/db/modifsBDD.sql not found" 
		echo "$__BASE [${LINENO}] : WARNING : Skipping database adjustments..."
	fi

        # deploiement pip requirement 
	# -----------
	if [ -e "${AppBuilDir}/requirements.txt" ]
	then
		echo "$__BASE [${LINENO}] : INFORMATION : File ${AppBuilDir}/requirements.txt exists"
		echo "$__BASE [${LINENO}] : INFORMATION : Installation Python Dependant Packages..."
		echo "-----------------------------------------------------------------------------"
		"$(sudo pip3 install -r ${AppBuilDir}/requirements.txt)" 
	else
		echo "$__BASE [${LINENO}] : ERROR : File ${AppBuilDir}/requirements.txt does not exists"
        fi

	# Reprise de la crontab (si option de mise à jour non activée)
	# -------------------------------------------------------------
	[ $__DEPLOY_CRON -eq 1 ] && releaseCron
}

# -------------------------------------------------------------------------
#   Function : UnzipRemDup
# -------------------------------------------------------------------------
# ARGUMENTS
#	$1 : ZipFile to deploy
# RETURNS
#     None
# -------------------------------------------------------------------------
UnzipRemDup()
{
	# Unzip build files
	# -----------------
	if [ -e $1 ] && [ $# -eq 1 ] 
	then
		#file ~/programmation/algocryptos/algocryptos_web/build/front.zip -b  -i
		local __ZIPDIR="$(cd "$(dirname "${1}")" && pwd)"
		local __ZIPFILE="${__ZIPDIR}/$(basename "${1}")"
		local __ZIPBASE="$(basename ${__ZIPFILE} .zip)"

		# On ne travail que si c'est un ZIP
		if [[ $(file -b --mime-type "${__ZIPFILE}") == "application/zip" ]] 
		then
			echo "$__BASE [${LINENO}] : INFORMATION : running unzip ${__ZIPFILE}" -d "${__ZIPDIR}/${__ZIPBASE}"
			unzip "${__ZIPFILE}" -d "${__ZIPDIR}/${__ZIPBASE}" 
			[ $? -eq 0 ] && echo "$__BASE [${LINENO}] : INFORMATION : ${__ZIPFILE} extracted successfully." || (echo "$__BASE [${LINENO}] : ERROR : Unzipping file faced an issue! " ; echo ${ERROR} )

			# Removing eventual duplicated directories
			# ----------------------------------------
			if [ "$(ls -1 "${__ZIPDIR}/${__ZIPBASE}" | wc -l)" -eq 1 ] && [ -d "${__ZIPDIR}/${__ZIPBASE}/${__ZIPBASE}" ]
			then
				echo "$__BASE [${LINENO}] : WARNING : dupicate subdirectory found! "
				echo "$__BASE [${LINENO}] : WARNING : moving All files from ${__ZIPDIR}/${__ZIPBASE}/${__ZIPBASE} to ${__ZIPDIR}/${__ZIPBASE}"
				$(mv "${__ZIPDIR}/${__ZIPBASE}" "${__ZIPDIR}/${__ZIPBASE}2Del/")
				$(mv "${__ZIPDIR}/${__ZIPBASE}2Del/${__ZIPBASE}" "${__ZIPDIR}/${__ZIPBASE}")
				echo "$__BASE [${LINENO}] : WARNING : Removing ${__ZIPDIR}/${__ZIPBASE}2Del directory"
				rmdir "${__ZIPDIR}/${__ZIPBASE}2Del/"
			else
				echo "$__BASE [${LINENO}] : INFORMATION : No duplicated directories found!"
			fi
		else
			echo "$__BASE [${LINENO}] : ERROR : Euh!!!! Comment ça c'est pas un ZIP!"
			exit $ERROR
		fi
	else
		echo "$__BASE [${LINENO}] : ERROR : Missing zip parameter !"
	       	exit $ERROR
	fi
	return $SUCCESS
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
	local AppFrontDir=""

	if [ -n $__AppRootDir ]
	then
		AppFrontDir="${__AppRootDir}/algocryptos_web"
		if [ -d ${AppFrontDir} ] && [ -d "${AppFrontDir}/.git" ]
		then
			echo "$__BASE [${LINENO}] : Application Front Directory ${AppFrontDir}"
			if [ -d  "${AppFrontDir}/build" ]
			then
				AppBuilDir="${AppFrontDir}/build"
			else
				echo "$__BASE [${LINENO}] : ERROR : Frontend build Directory ${AppBuilDir} does not exist!"
				echo "$__BASE [${LINENO}] : ERROR : Please check you app root directory or initialise the frontend git by:"
				echo "$__BASE [${LINENO}] : ERROR : '--> git clone <git repository>"
				exit ${ERROR}
			fi
		else
			echo "$__BASE [${LINENO}] : ERROR : ${AppFrontDir} does not exist or is not a git local repository!"
			echo "$__BASE [${LINENO}] : ERROR : Please check you app root directory or initialise the git by:"
			echo "$__BASE [${LINENO}] : ERROR : '--> git clone <git repository>"
			exit ${ERROR}
		fi
	else
	      	echo "$__BASE [${LINENO}] : ERROR : App working directory set to ${__AppRootDir}"
		exit ${ERROR}
	fi
	
	# Retrieve Github
	# ---------------
	echo "$__BASE [${LINENO}] : INFORMATION : Front End - Git retrieval)" 
	Gitpull ${AppFrontDir}

	echo "$__BASE [${LINENO}] : INFORMATION : DEPLOIEMENT DU FRONTEND $(pwd)" 

	# Backup OldDirectory in Case of Failback
	# ---------------------------------------
	########	echo "$__BASE [${LINENO}] : INFORMATION : Removing old backup file"

	echo "$__BASE [${LINENO}] : INFORMATION : Backup Current Server and Front directory !"
	echo "$__BASE [${LINENO}] : INFORMATION : Useful in case of failback"
	
	[ -d "${AppBuilDir}/server" ] && mv "${AppBuilDir}/server" "${AppBuilDir}/server_bkp_${DATETIME}" || echo "No ${AppBuilDir}/server found! skipping backup" 
	[ -d "${AppBuilDir}/front" ] && mv "${AppBuilDir}/front" "${AppBuilDir}/front_bkp_${DATETIME}" || echo "No ${AppBuilDir}/front found! skipping backup" 

	# Unzip build files
	# -----------------

	# FrontEnd
	UnzipRemDup "${AppBuilDir}/front.zip"

	# Backend
	UnzipRemDup "${AppBuilDir}/server.zip"
	
	# We validate that a RootDirectory is set
	#if [ -n $__AppRootDir ] 
	#then
	#	AppBuilDir="${__AppRootDir}/algocryptos_web/build"

		if [ $# -gt 0 ] && [ -n $1 ]
		then
			ToPushDir="${1}"
		else
			ToPushDir="${AppBuilDir}/front"
		fi

		if [ $# -gt 0 ] && [ -n $2 ]
		then
			S3Bucket="${2}"
		else
			S3Bucket="s3://algocrypto"
		fi
		aws s3 sync ${ToPushDir} ${S3Bucket} 
	#else 

	#	echo "$__BASE [${LINENO}] : ERROR : AWS Sync Not possible !!!"
	#	echo "$__BASE [${LINENO}] : ERROR : App working directory set to ${__AppRootDir}"
	#	exit ${__ERROR}
	#fi

	#starting NodeJs
	echo "$__BASE [${LINENO}] : INFORMATION : Reloading PM2 www NodeJS applcation!"
	pm2 reload www
	return ${SUCCESS}
}


##########################################################################################
#
# MAIN - Script execution really Starts here
#
##########################################################################################

# Parameters parsing
# ------------------
while getopts ":abcfhV" option
do
	# Without options it will do a full deployment unless, we reset to have a only on action
	### !!! echo "OPTIND : in the getopts :  ${OPTIND}"
	if [ $OPTIND -eq 2 ] 
	then
		__DEPLOY_FRONT=1
		__DEPLOY_BACK=1
		__DEPLOY_CRON=1
	fi

	case "${option}" in
		a)				# Deploy all part of AlgoCrypto Application
			__DEPLOY_BACK=0
			__DEPLOY_CRON=0
			__DEPLOY_FRONT=0
			;;		
		b)				# Deploy Only the Back-end
			__DEPLOY_BACK=0
			;;
		c)
			__DEPLOY_CRON=0
			;;
		f)				# Deploy Only the Front-end
			__DEPLOY_FRONT=0
			;;
		h)			# Usage
			usage	|| return ${ERROR}
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
		echo "$__BASE [${LINENO}] : INFORMATION : App working directory set to ${__AppRootDir}"
	else
		echo "$__BASE [${LINENO}] : ERROR : $1 is not a directory or does not exists"
	fi
else
	echo "$__BASE [${LINENO}] : ERROR : Missing Mandatory argument working Directory"
	echo "$__BASE [${LINENO}] : INFO  : '--> autodeploy.sh <App working directory>"
	exit ${ERROR}
fi

if [ ${__DEPLOY_BACK} -eq 0 ]
then
	#deploy Backend following the define sequence
	DeployBackend
fi

if [ ${__DEPLOY_CRON} -eq 0 ]
then
	#deploy Backend following the define sequence
	stopCron	
	NewCron="${__AppRootDir}/algocryptos_scripts/scripts/scripts.txt"
	releaseCron ${NewCron}
fi

if [ ${__DEPLOY_FRONT} -eq 0 ]
then
	DeployFront
fi

__EXIT_STATUS=$SUCCESS

