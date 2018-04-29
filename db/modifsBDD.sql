INSERT INTO public.alert_type(
	id_alert_type, global_alert, category_type, filter_type,  trigger_period_hour, description)
	VALUES (2, false, 'volume', 'TOP100', '1', '[Crypto Top 100][Mean vol. 1h/30d > 800%] #crypto_name# (#crypto_symbol#): #val1_double#%');