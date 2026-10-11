# Elise : adaptation des icones lors de l'ouverture de Writer.
# Ce composant ne modifie ni les documents ni les macros Basic.
# Version 1.1.0 de test ; mise a jour au prochain evenement d'ouverture,
# mais pas de surveillance continue du theme (prevue pour une autre etape).
import os
import uno
import unohelper
from com.sun.star.task import XJob

IMPLEMENTATION = 'com.pdias79.elise.appearance.Job'
EXTENSION_ID = 'com.pdias79.elise'
WRITER_MODULE = 'com.sun.star.text.TextDocument'

# Lie exactement les URL des commandes aux fichiers SVG de l'OXT.
ICON_FILES = (
    ('macro:///elise.format.EncadrerTexteEnRouge', 'Encadrer_Rouge.svg'),
    ('macro:///elise.format.EncadrerTexteEnVert', 'Encadrer_Vert.svg'),
    ('macro:///elise.format.EncadrerTexteEnBleu', 'Encadrer_Bleu.svg'),
    ('macro:///elise.format.EncadrerTexteEnRose', 'Encadrer_Rose.svg'),
    ('macro:///elise.format.EncadrerTexteEnJaune', 'Encadrer_Jaune.svg'),
    ('macro:///elise.format.EncadrerTexteEnNoir', 'Encadrer_Noir.svg'),
    ('macro:///elise.format.SupprimerEncadrementTexte', 'Rien.svg'),
    ('macro:///elise.format.SoulignerTexteEnRouge', 'Souligner_Rouge.svg'),
    ('macro:///elise.format.SoulignerTexteEnVert', 'Souligner_Vert.svg'),
    ('macro:///elise.format.SoulignerTexteEnBleu', 'Souligner_Bleu.svg'),
    ('macro:///elise.format.SoulignerTexteEnRose', 'Souligner_Rose.svg'),
    ('macro:///elise.format.SoulignerTexteEnJaune', 'Souligner_Jaune.svg'),
    ('macro:///elise.format.SoulignerTexteEnNoir', 'Souligner_Noir.svg'),
    ('macro:///elise.format.SurlignerTexteEnRouge', 'Surligner_Rouge.svg'),
    ('macro:///elise.format.SurlignerTexteEnVert', 'Surligner_Vert.svg'),
    ('macro:///elise.format.SurlignerTexteEnBleu', 'Surligner_Bleu.svg'),
    ('macro:///elise.format.SurlignerTexteEnRose', 'Surligner_Rose.svg'),
    ('macro:///elise.format.SurlignerTexteEnJaune', 'Surligner_Jaune.svg'),
    ('macro:///elise.format.SurlignerTexteEnNoir', 'Surligner_Noir.svg'),
    ('macro:///elise.format.SupprimerSurlignageTexte', 'Rien.svg'),
    ('macro:///elise.format.InsererDateCours', 'Calendrier.svg'),
)


# Un changement de document ne recharge pas les icones deja appliquees.
_last_applied = None


def _property(name, value):
    prop = uno.createUnoStruct('com.sun.star.beans.PropertyValue')
    prop.Name = name
    prop.Value = value
    return prop


def _appearance_mode(ctx):
    provider = ctx.ServiceManager.createInstanceWithContext(
        'com.sun.star.configuration.ConfigurationProvider', ctx)
    config = provider.createInstanceWithArguments(
        'com.sun.star.configuration.ConfigurationAccess',
        (_property('nodepath', '/org.openoffice.Office.Common/Appearance'),))
    return int(config.getPropertyValue('ApplicationAppearance'))


def _windows_dark_mode():
    # Respecter le parametre Applications de Windows lorsque LibreOffice est
    # regle sur Automatique. En cas de lecture impossible : conserver le clair.
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r'Software\Microsoft\Windows\CurrentVersion\Themes\Personalize')
        try:
            light, _ = winreg.QueryValueEx(key, 'AppsUseLightTheme')
            return int(light) == 0
        finally:
            winreg.CloseKey(key)
    except (ImportError, OSError, ValueError, TypeError):
        return False


def _is_dark(ctx):
    mode = _appearance_mode(ctx)
    if mode == 2:
        return True
    if mode == 1:
        return False
    if os.name == 'nt':
        return _windows_dark_mode()
    return False  # Approche de repli Linux/macOS en mode automatique.


def _apply(ctx):
    global _last_applied
    dark = _is_dark(ctx)
    if _last_applied is not None and _last_applied == dark:
        return

    pkg_info = ctx.getValueByName(
        '/singletons/com.sun.star.deployment.PackageInformationProvider')
    base = pkg_info.getPackageLocation(EXTENSION_ID).rstrip('/')
    if not base:
        return

    sm = ctx.ServiceManager
    graphics = sm.createInstanceWithContext('com.sun.star.graphic.GraphicProvider', ctx)
    supplier = sm.createInstanceWithContext(
        'com.sun.star.ui.ModuleUIConfigurationManagerSupplier', ctx)
    ui = supplier.getUIConfigurationManager(WRITER_MODULE)
    manager = ui.getImageManager()

    loaded = []
    for command, filename in ICON_FILES:
        subdir = 'icons/dark/' if dark else 'icons/light/'
        graphic = graphics.queryGraphic((_property('URL',base+'/'+subdir+filename),))
        if graphic is not None:
            loaded.append((command, graphic))
    if not loaded:
        return

    successes = 0
    # Grandes et petites images sont des entrees distinctes dans XImageManager.
    for size in (0, 1, 2):
        # insertImages ecrase uniquement les cles qui n'existent pas encore.
        # Eviter l'echec d'un lot mixte : inserer/remplacer au cas par cas.
        for cmd, graphic in loaded:
            try:
                if manager.hasImage(size, cmd):
                    manager.replaceImages(size, (cmd,), (graphic,))
                else:
                    manager.insertImages(size, (cmd,), (graphic,))
                successes += 1
            except Exception:
                # Certaines tailles ne sont pas supportees par toutes les versions.
                continue
    if successes:
        _last_applied = dark


class EliseAppearanceJob(unohelper.Base, XJob):
    def __init__(self, context):
        self.ctx = context

    def execute(self, args):
        try:
            _apply(self.ctx)
        except Exception:
            # Jamais bloquer l'ouverture d'un document pour une icone.
            pass
        return None


g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationHelper.addImplementation(
    EliseAppearanceJob, IMPLEMENTATION, ('com.sun.star.task.Job',))
