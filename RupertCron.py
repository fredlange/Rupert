## Cronjob
import yahoo_data_handler as ydh
import RupertReport as rr
import RupertMail

def cron():
    ydh.collect_batch_data('OMX-ST.txt')
    rr.runReport('Stocklists/OMX-ST-30.txt')
    RupertMail.sendEmailToAdmin("Download CSV data complete", "CSV archive has been updated. \n // Rupert")


if __name__ == "__main__":
    cron()
