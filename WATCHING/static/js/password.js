$(document).ready(() => {
  $("#inputPw_give").focus();
});

$(".navbar_userMenu").click(() => {
  $(".detailBox").slideToggle(100);
});

const change_info = () => {
  alert("비밀번호를 변경해 봤습니다");
};
