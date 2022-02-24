// 첫 시작 id input에 focus
$(document).ready(() => {
  $("#id").focus();
});

// 회원가입 데이터 POST (유효성 검사)
const save_order = () => {
  let id = $("#id").val();
  let password = $("#password").val();
  let RegExp = /^[a-zA-z0-9]{4,12}$/;
  if (RegExp.test(id) === false) {
    alert("아이디는 4~12자리의 영대소문자와 숫자로 입력해주세요");
    return false;
  } else if (RegExp.test(password) === false) {
    alert("비밀번호는 4~12자리의 영대소문자와 숫자로 입력해주세요");
    return false;
  }
  $.ajax({
    type: "POST",
    url: "/signup",
    data: { id_give: id, password_give: password },
    success: (response) => {
      if (response.result === "success") {
        alert(response.msg);
        location.href = "/";
      } else {
        alert(response.msg);
        location.reload();
      }
    },
  });
};
