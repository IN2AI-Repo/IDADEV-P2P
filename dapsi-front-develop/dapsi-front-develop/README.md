
# Dapsi - Front

### Technologies

* [Vue.js](https://vuejs.org/)
* [Electron builder](https://www.electron.build/)
* [Tailwindcss](https://tailwindcss.com/) 
* [Vue cli](https://cli.vuejs.org/)

## Project setup

Before starting, having [npm](https://www.npmjs.com/get-npm) or [yarn](https://classic.yarnpkg.com/en/docs/install/#mac-stable) installed, to install all the dependencies execute the following command

```yarn install``` or ```npm i```

  

### Compile and run in develop mode

```yarn serve``` or ```npm run serve```

  

### Compile for production

When the project has been compiled it will be saved in the dist folder

```yarn build``` or ```npm run build```


###  Compile and run in electron develop mode


```
yarn electron:serve
``` 
or 
```
npm run electron:serve
```

  

###  Compile for multiplatform production with electron

To compile the project to their respective operating systems, the following commands must be executed

> Windows

```
yarn electron:build -w
``` 
or 
```
npm run electron:build -w
```


> Linux

```
yarn electron:build -l
``` 
or 
```
npm run electron:build -l
```


> Mac

```
yarn electron:build -m
``` 
or 
```
npm run electron:build -m
```

 More info about Electron [Configuration Reference](https://www.electron.build/cli).
  
