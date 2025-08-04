# -*- coding: utf-8 -*-
import os
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtWidgets import QAction
from qgis.PyQt.QtGui import QIcon
from .microplot_generator_dialog import MicroplotGeneratorDialog

class MicroplotGenerator:
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        
        # Initialize translator
        locale = QSettings().value('locale/userLocale', 'en_US')
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'microplot_generator_{}.qm'.format(locale[0:2]))

        self.translator = None
        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        self.actions = []
        self.menu = QCoreApplication.translate('MicroplotGenerator', '&Magic Microplots Shape Generator – UAV')

    def initGui(self):
        icon_path = os.path.join(self.plugin_dir, 'icon.svg')
        
        action_text = QCoreApplication.translate('MicroplotGeneratorDialogBase', 'Create Microplots Grid')
        
        self.action = QAction(
            QIcon(icon_path),
            action_text,
            self.iface.mainWindow())
            
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(self.menu, self.action)

    def unload(self):
        if self.translator:
            QCoreApplication.removeTranslator(self.translator)

        self.iface.removePluginMenu(self.menu, self.action)
        self.iface.removeToolBarIcon(self.action)

    def run(self):
        self.dialog = MicroplotGeneratorDialog(iface=self.iface)
        self.dialog.show()