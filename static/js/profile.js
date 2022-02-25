$(".navbar_userMenu").click(() => {
  $(".detailBox").slideToggle(100);
});

const change_info = () => {
  nowpw = $("#inputPw_give").val();
  chgpw = $("#changePw_give").val();
  let form = new FormData();
  form.append("file", $("#file_upload")[0].files[0]);
  $.ajax({
    url: "/file_upload",
    type: "POST",
    processData: false,
    contentType: false,
    data: form,
    success: (response) => {
      if (response.result == "success") {
        const uploadFile = response.upload_flag;
        if (uploadFile === "n") {
          alert("변경 사항이 없습니다");
        } else {
          $.ajax({
            type: "POST",
            url: "/edit",
            data: { inputPw_give: nowpw, changePw_give: chgpw },
            success: (response) => {
              if (response.result === "success") {
                alert(response.msg);
                location.reload();
              }
            },
          });
        }
      }
    },
  });
};
