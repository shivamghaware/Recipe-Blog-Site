const submit=document.querySelector('#submit');

submit.addEventListener('click', function(event){
    let a=confirm('Are you sure to submit the recipe?');
    if(a){

    }
    else{
        event.preventDefault();
    }
})