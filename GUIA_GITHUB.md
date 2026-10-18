# Guía rápida: subir el proyecto a GitHub

El repositorio Git ya está inicializado localmente con 6 commits temáticos.
Para publicarlo en **tu** cuenta de GitHub y obtener el enlace de revisión:

### Opción A — con GitHub CLI (`gh`)
```bash
cd proyecto
gh auth login
gh repo create redconecta-telecom-ciencia-datos --public --source=. --remote=origin --push
```

### Opción B — manual (crear el repo en la web primero)
1. Crea un repositorio vacío en https://github.com/new
   (por ejemplo: `redconecta-telecom-ciencia-datos`), sin README.
2. Luego ejecuta:
```bash
cd proyecto
git remote add origin https://github.com/TU_USUARIO/redconecta-telecom-ciencia-datos.git
git branch -M main
git push -u origin main
```

El enlace a incluir en el informe será:
`https://github.com/TU_USUARIO/redconecta-telecom-ciencia-datos`

### Verificar el historial de commits
```bash
git log --oneline
```
