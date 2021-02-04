class HardNut {
    
    constructor(base_url){    
        if (base_url.substr(-1) != '/') base_url += '/';
        this.base_url = base_url
        this.authenticated = false
        this.hook_login = null
    }


    logout(){
        fetch(this.base_url + 'logout', {method: 'POST', credentials: 'include'})
        .then( r=> {
            if(r.status == 200){
                console.log("logout ok")
            }
            this.authenticated=false
            this.update_page()    
        })
        .catch(e => {
            console.log("logout error", e)
        })
    }

    update_page(){

        var visible;

        if(this.authenticated === null){
            visible = "hardnut-authenticating"
        }else if(this.authenticated){
            visible = "hardnut-authenticated"
        }else{
            visible = "hardnut-unauthenticated"
        }

        //console.log("visible:", visible)

        for(let classname of ['hardnut-authenticating', 'hardnut-authenticated', 'hardnut-unauthenticated']){
            let display = (classname == visible) ? 'block' : 'none'            
            //console.log("set", classname, display)
            for(let e of document.getElementsByClassName(classname)){
                //console.log("update", e)
                e.style.display = display
            }    
        }

        for(let e of document.getElementsByClassName('hardnut-onload')){            
            e.style.display = 'block'
        }                
    }

    check_login(){
        this.authenticated = null
        this.update_page()
        fetch(this.base_url + 'authenticated', {credentials: 'include'})
        .then( r=> {
          if(r.status == 200){
            this.authenticated = true
            if(this.hook_login){
                this.hook_login()
            }
            this.update_page()
            }
          if(r.status == 401){
            this.authenticated = false
            this.update_page()            
            }
        })
        .catch( e => {
          console.log("catch", e)
        })
    }
    

    get(path){
        return fetch(this.base_url + path, {credentials: 'include'})
    }

    put(path, data){
        return fetch(this.base_url + path, 
            {
                credentials: 'include', 
                method: 'PUT', 
                body: data
            })
    }

    get_json_file(path, code){
        fetch(this.base_url + path, {credentials: 'include'})
        .then( r => {
            return r.json()
        })
        .then(data => {code(data)})
    }
}
