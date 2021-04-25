import datetime
import time
from datetime import timedelta

import xbmc
import xbmcaddon

ADDON = xbmcaddon.Addon(id='plugin.video.imdb.watchlists')


def subscription_update():
    if ADDON.getSetting('subscription_update') == "true":
        return True
    else:
        return False


def update_tv():
    if ADDON.getSetting('update_tv') == "true":
        return True
    else:
        return False


def update_watchlists():
    if ADDON.getSetting('update_watchlists') == "true":
        return True
    else:
        return False


def subscription_timer():
    return int(ADDON.getSetting('subscription_timer'))


class AutoUpdater:
    def update(self):
        hours_list = [2, 5, 10, 15, 24]
        hours = hours_list[subscription_timer()]
        xbmc.log('[IMDb Watchlists] Updating', level=xbmc.LOGINFO)
        time.sleep(1)
        if update_watchlists():
            xbmc.log('[IMDb Watchlists] Updating Watchlists', level=xbmc.LOGINFO)
            xbmc.executebuiltin('RunPlugin(plugin://plugin.video.imdb.watchlists/update_watchlists)')
        if update_tv():
            xbmc.log('[IMDb Watchlists] Updating TV Shows', level=xbmc.LOGINFO)
            xbmc.executebuiltin('RunPlugin(plugin://plugin.video.imdb.watchlists/update_tv)')
        now = datetime.datetime.now()
        ADDON.setSetting('service_time', str(now + timedelta(hours=hours)).split('.')[0])
        xbmc.log("[IMDb Watchlists] Library updated. Next run at " + ADDON.getSetting('service_time'),
                 level=xbmc.LOGINFO)
        monitor = xbmc.Monitor()
        if ADDON.getSetting('update_main') == "true":
            while xbmc.getCondVisibility('Library.IsScanningVideo'):
                time.sleep(1)
                if monitor.abortRequested():
                    return
            xbmc.log('[IMDb Watchlists] Updating Kodi Library', level=xbmc.LOGINFO)
            xbmc.executebuiltin('UpdateLibrary(video)')
        if ADDON.getSetting('update_clean') == "true":
            time.sleep(1)
            while xbmc.getCondVisibility('Library.IsScanningVideo'):
                time.sleep(1)
                if monitor.abortRequested():
                    return
            xbmc.log('[IMDb Watchlists] Cleaning Kodi Library', level=xbmc.LOGINFO)
            xbmc.executebuiltin('CleanLibrary(video)')

    def run_program(self):
        if ADDON.getSetting('login_update') == "true":
            delay = int(ADDON.getSetting('login_delay'))
            time.sleep(delay * 60)
            self.update()
        monitor = xbmc.Monitor()
        while not monitor.abortRequested():
            if monitor.waitForAbort(10):
                break
            if subscription_update():
                try:
                    next_run = datetime.datetime.fromtimestamp(time.mktime(
                        time.strptime(ADDON.getSetting('service_time'), "%Y-%m-%d %H:%M:%S")))
                    now = datetime.datetime.now()
                    if now > next_run:
                        self.update()
                except Exception as detail:
                    xbmc.log("[IMDb Watchlists] Update Exception %s" % detail, level=xbmc.LOGERROR)
                    pass


xbmc.log("[IMDb Watchlists] Subscription service starting...", level=xbmc.LOGINFO)
AutoUpdater().run_program()
