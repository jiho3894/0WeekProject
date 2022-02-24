// 첫 시작 id input에 focus
$(document).ready(() => {
  $("#id").focus();
});

// 회원가입 데이터 POST (유효성 검사)
const save_order = () => {
  alert("회원가입 완료");
  location.href = "index.html";
};
