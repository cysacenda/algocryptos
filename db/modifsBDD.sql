INSERT INTO public.alert_type(
	id_alert_type, global_alert, category_type, filter_type,  trigger_period_hour, description)
	VALUES (3, false, 'reddit', 'ALL', '24', '[Crypto All][Reddit subscribers trend 1d] #crypto_name# (#crypto_symbol#): #val1_double#%');