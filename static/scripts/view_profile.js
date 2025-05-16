const button=document.querySelector('#delete_button')

button.addEventListener('click', function(event){
    let a=confirm('Are you sure to delete this blog?');
    if(a){
        window.location.href = '/delete_recipe/{{ blog_id }}';
    }
    else{
        event.preventDefault();
    }
})