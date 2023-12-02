# PluginBase
a meta plugin base in python

## Pack

This command with make a dist directory with a binary file in it  
```bash
pyinstaller run.spec
```

Copy the binary file into the current directory
```bash
// macos
cp ./dist/run ./

// windows
cp ./dist/run.exe ./
```

Run the binary file
```bash
//macos
./run

//windows
./run.exe
```

## Tips  
If you want to add hiddenimport to the project, you can edit `run.spec` file 
and add the labery into the `hiddenimport` feild  