# coding:utf8

from syncplay.players.basePlayer import BasePlayer
from syncplay import constants
from syncplay.messages import getMessage
from kodipydent import Kodi


class KodiPlayer(BasePlayer):
    speedSupported = False  # supported speeds FWD/BACK 1x,2x,4x,8x,16x,32x, until implemented setting as not supported
    customOpenDialog = False
    alertOSDSupported = False
    chatOSDSupported = False

    def __init__(self, client, playerPath, filePath, args):
        self._client = client
        self._paused = None
        self._position = 0.0
        self._duration = None
        self._filename = None
        self.quitReason = None
        self.lastLoadedTime = None
        self.fileLoaded = False
        self.delayedFilePath = None

        self._kodiHost = self.getParamValue(args, 'kodiHost', '127.0.0.1')
        self._kodiPort = self.getParamValue(args, 'kodiPort', 8080)
        self._kodiUser = self.getParamValue(args, 'kodiUser', 'kodi')
        self._kodiPass = self.getParamValue(args, 'kodiPass', '1234')

        try:
            self.kodipydent = Kodi(self._kodiHost, port=self._kodiPort, username=self._kodiUser, password=self._kodiPass)
        except ValueError:
            return

    @staticmethod
    def getParamValue(args, param, default):
        for p in args:
            if p.startswith("%s=" % param):
                return p[len(param)+1:]
        return default

    @staticmethod
    def run(client, playerPath, filePath, args):
        kodiplayer = KodiPlayer(client, KodiPlayer.getExpandedPath(playerPath), filePath, args)
        return kodiplayer

    @staticmethod
    def getDefaultPlayerPathsList():
        lpaths = []
        return lpaths

    @staticmethod
    def getIconPath(path):
        return constants.KODI_ICONPATH

    @staticmethod
    def getPlayerPathErrors(playerPath, filePath):
        if not filePath:
            return getMessage("no-file-path-config-error")

    @staticmethod
    def getExpandedPath(playerPath):
        return playerPath

    def askForStatus(self):
        x = self.kodipydent.Player.GetProperties(playerid=1, properties=['time', 'speed'])
        # convert
        self._position = (x['result']['time']['hours'] * 3600) + \
                         (x['result']['time']['minutes'] * 60) + \
                         (x['result']['time']['seconds']) + \
                         (x['result']['time']['milliseconds'] / 1000.0)
        self._client.updatePlayerStatus((x['result']['speed'] != 0.0), self._position)

    # sends message to player to display on screen
    def displayMessage(self, message, duration=(constants.OSD_DURATION * 1000), secondaryOSD=False,
                       mood=constants.MESSAGE_NEUTRAL):
        # kodi requires minimum display time of 1500ms
        d = max(1500, duration)
        # only types of messages in Kodi are info/warning/error
        t = 'info'
        if mood == constants.MESSAGE_BADNEWS:
            t = 'error'
        if mood == constants.MESSAGE_NEUTRAL:
            t = 'info'
        if mood == constants.MESSAGE_GOODNEWS:
            # there's no appropriate message type in Kodi and I don't think we should map it to warning (last one
            # left)? :(
            t = 'info'

        self.kodipydent.GUI.ShowNotification(title='Message', message=message, displaytime=d, image=t)

    def drop(self):
        pass

    # pauses/unpauses and updates status (boolean)
    def setPaused(self, value):
        self.kodipydent.Player.PlayPause(playerid=1, play=not value)
        self.askForStatus()

    def setFeatures(self, featureList):
        pass

    # sets position in seconds (float)
    def setPosition(self, value):
        # convert seconds to dictionary
        x = {'hours': round(value / 3600), 'minutes': round((value % 3600) / 60), 'seconds': round((value % 60)),
             'miliseconds': round(value * 1000.0) % 1000}

        self.kodipydent.Player.Seek(playerid=1, value=x)

    # sets speed (float value)
    def setSpeed(self, value):
        # allowed values are 1,2,4,8,16,32x FORWARD, and -1,-2,-4,-8,-16,-32 (BACKWARDS)
        # as speeds such as .5 are not supported by API, feature set as not implemented.
        # If/when support for slow playback is added to Kodi, uncomment following line
        # and remove pass.
        # self.kodipydent.Player.SetSpeed(playerid=1, speed=value)
        pass

    def openFile(self, filePath, resetPosition=False):
        pass

    @staticmethod
    def isValidPlayerPath(path):
        if path == '/dev/kodi':
            return True
        return False

    @staticmethod
    def openCustomOpenDialog(self):
        pass
