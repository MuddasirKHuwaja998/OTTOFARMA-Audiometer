## File for long texts ##

text_Familiarization = """
Segue una breve fase di familiarizzazione in cui puoi familiarizzare con il programma.
Questi test non sono inclusi nei risultati successivi e servono solo a verificare se hai compreso la procedura.
Sentirai sequenze di toni con volumi e frequenze diverse. Per favore
premi immediatamente la barra spaziatrice ogni volta che senti un tono. Nota che
non riceverai alcun feedback dal programma: è normale.\n
Utilizzo presso OtofarmaSpa:\n
- Screening breve: può essere utilizzato per il triage dei pazienti o per controlli di routine.
- Audiogramma classico: adatto per diagnosi approfondite da parte di audiologi o specialisti dell'udito.\nUn audiogramma diagnostico completo, che misura le soglie uditive su una gamma di frequenze
- Calibrazione: richiesta regolarmente per mantenere la conformità agli standard medici.\n(Questo non funziona ancora come da requisiti, presto inizierà a funzionare.)
"""

text_calibration = """Specificare un valore a cui deve essere eseguita la calibrazione (nota: con un sistema non calibrato, potrebbero essere emessi toni inaspettatamente forti!).

Avviare la calibrazione. Viene emesso un tono sinusoidale a 125 Hz per 10 secondi. È possibile interrompere la riproduzione in qualsiasi momento
o riprodurre nuovamente il tono.

Inserire il valore misurato nel campo sottostante. Premere Ora fare clic su "Frequenza successiva" e fare lo stesso per tutte le frequenze successive.

I toni sinusoidali da 125 Hz a 8000 Hz vengono testati in intervalli di ottava.

Prima a sinistra e poi a destra. Dopo che l'ultima frequenza è stata calibrata, viene creato un file csv con i valori di calibrazione."""