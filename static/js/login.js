// 첫 시작 로그인 input에 focus
$(document).ready(() => {
  $("#id").focus();
});

const login = () => {
  let inputId = $("#id").val();
  let inputPw = $("#password").val();
  if (inputId == "" || inputPw == "") {
    alert("아이디, 비밀번호를 정확히 입력해주세요");
    return false;
  }
  $.ajax({
    type: "POST",
    url: "/login_check",
    data: {
      id_give: inputId,
      password_give: inputPw,
    },
    success: (response) => {
      if (response.result == "success") {
        location.href = "/main";
      } else {
        alert(response.msg);
        location.reload();
      }
    },
  });
};
