# MonExtension — Barre d'outils LibreOffice Writer

## Structure
```
MonExtension/
├── META-INF/
│   └── manifest.xml          ← déclare tous les fichiers
├── Basic/
│   └── MonExtension/
│       ├── script.xlb        ← index de la bibliothèque Basic
│       └── Module1.xba       ← vos macros (CDATA StarBasic)
├── icons/
│   ├── btn01.png … btn12.png ← icônes 26×26 px (ou 16×16)
├── Addons.xcu                ← définition de la toolbar
├── description.xml           ← métadonnées de l'extension
└── build.sh                  ← script de construction
```

## Personnalisation

### 1. Identifiant unique
Dans `description.xml` et `Addons.xcu`, remplacez :
```
com.monentreprise.monextension
```
par un identifiant qui vous appartient (ex: `fr.maville.monoutil`).

### 2. Noms des macros
Dans `Addons.xcu`, chaque bouton pointe vers :
```
macro:///MonExtension.Module1.Macro01
         └─ bibliothèque  └─ module  └─ nom du Sub
```
Modifiez pour correspondre à vos Sub existants.

### 3. Icônes
- Copiez vos PNG dans `icons/`
- Taille recommandée : **26×26 px** (HiDPI) ou 16×16 px
- Nommez-les exactement comme référencé dans `Addons.xcu`

### 4. Plusieurs modules
Si vos macros sont dans plusieurs modules, ajoutez dans `script.xlb` :
```xml
<library:element library:name="Module2"/>
```
et créez `Module2.xba` sur le même modèle.

### 5. Séparateurs
Un séparateur dans la toolbar s'ajoute avec :
```xml
<node oor:name="SeparatorXX" oor:op="replace">
  <prop oor:name="URL" oor:type="xs:string">
    <value>private:separator</value>
  </prop>
  <prop oor:name="Target" oor:type="xs:string"><value>_self</value></prop>
</node>
```

## Construction et installation
```bash
cd MonExtension/
bash build.sh
# → MonExtension.oxt
```
Puis dans LibreOffice :
**Outils → Gestionnaire d'extensions → Ajouter → sélectionner MonExtension.oxt**
