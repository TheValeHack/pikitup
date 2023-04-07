$("#btn").on("click", function(){
    $(".sidebar").toggleClass("open");
    menuBtnChange();
});

function menuBtnChange() {
    if($(".sidebar").hasClass("open")){
        $("#btn").addClass("bx-menu-alt-right").removeClass("bx-menu");
    }else {
        $("#btn").addClass("bx-menu").removeClass("bx-menu-alt-right");
    }
}
$("#trashphoto").change(function(){
    let trashphotobox = ""
    for(let i=0;i<this.files.length;i++){
       trashphotobox += `<div class="trash-photo-box">${this.files[i].name}</div>`
    }
    $(".trash-photos-list").html(trashphotobox)
});
$("#driverstip").change(function(){
    let drivertip = $("#driverstip").val()
    if($("#driverstip").val() == "") drivertip = "0"
    $("#modalorder #totalpayments .summary-value").text(drivertip)
    $("#modalorder #driverstipmodal").text(drivertip)
})
$("#orderbutton").click( function() {
   $('#orderform').submit();
}); 
$(".removetrash").on("click", function(){
    let trashId = $(this).attr("id")
    console.log(trashId)
    Swal.fire({
        title: 'Are you sure?',
        text: "Trash will be removed permanently!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Yes, remove it!'
      }).then((result) => {
        if (result.isConfirmed) {
          Swal.fire(
            'Removed!',
            'Your trash has been removed.',
            'success'
          )
        }
      })
})