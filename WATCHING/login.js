// 첫 시작 로그인 input에 focus
$(document).ready(() => {
  $("#id").focus();
});

const login = () => {
  alert("로그인 완료");
  location.href = "main.html";
};
