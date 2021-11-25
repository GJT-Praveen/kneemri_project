function toggle_menu(){
    let toggle = document.querySelector('.toggle');
    let navigation = document.querySelector(".navigation");
    let main = document.querySelector('.main');
    
    toggle.classList.toggle('active');
    navigation.classList.toggle('active');
    main.classList.toggle('active');  
}
setTimeout(function(){
    $('.alert').removeClass("show");
    $('.alert').addClass("hide");
    },2000);
$('.close-btn').click(function(){
    $('.alert').removeClass("show");
    $('.alert').addClass("hide");
  });