$(document).ready(() => {
  $("#inputPw_give").focus();
});

$(".navbar_userMenu").click(() => {
  $(".detailBox").slideToggle(100);
});

const change_info = () => {
  nowpw = $("#inputPw_give").val();
  chgpw = $("#changePw_give").val();
  let RegExp = /^[a-zA-z0-9]{4,12}$/;
  if (RegExp.test(nowpw) === false) {
    if (nowpw === "") {
      console.log(".");
    } else {
      alert("비밀번호는 4~12자리의 영대소문자와 숫자로");
      return false;
    }
  } else if (RegExp.test(chgpw) === false) {
    if (chgpw !== "") {
      alert("비밀번호는 4~12자리의 영대소문자와 숫자로");
      return false;
    }
  }
  $.ajax({
    type: "POST",
    url: "/edit",
    data: { inputPw_give: nowpw, changePw_give: chgpw },
    success: (response) => {
      if (response.pw_ch_flag === "n") {
        if (response.msg == "비밀번호가 정상적으로 변경되었습니다.") {
          alert(response.msg);
          location.href = "/";
        } else {
          alert("양식에 맞게 입력해주세요");
        }
      } else {
        alert(response.msg);
        location.reload();
      }
    },
  });
};
