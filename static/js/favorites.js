$(".navbar_userMenu").click(() => {
  $(".detailBox").slideToggle(100);
});

const favorite = (num) => {
  const favorite = $(".favorite")[num];
  const title = favorite.querySelector(".movie-title").innerHTML;
  const id = favorite.querySelector(".movie_id").innerHTML;
  const overview = favorite.querySelector(".movie-desc-simple").innerHTML;
  const poster = favorite
    .querySelector(".slid_movie")
    .style.backgroundImage.split('"')[1];
  $.ajax({
    type: "POST",
    url: "/manage_star",
    data: {
      movie_id_give: id,
      movie_title_give: title,
      poster_path_give: poster,
      movie_overview_give: overview,
      oder_flag_give: "delete",
    },
    success: (response) => {
      alert(response.msg);
      location.reload();
    },
  });
};

$.ajax({
  type: "GET",
  url: "/star_load",
  success: (response) => {
    response.favorites_list.map((data, index) => {
      const movie_id = data.movie_id;
      const image_path = data.poster_path;
      const movie_title = data.movie_title;
      const movie_overview = data.movie_overview;
      let temp_html = `<div  class="favorite">
        <div class="slid_movie" style=" background-image: url('${image_path}')"></div>
        <div class="movie_desc">
            <p style="display:none;" class="movie_id">${movie_id}</p>
            <div class="movie_header">
              <p class="movie-title">${movie_title}</p>
              <button onclick="favorite(${index})" class="favor-btn">❌</button>
            </div>
            <div class="playBtnContainer"><button class="playBtn">시청하기</button></div>
            <p class="movie-desc-simple">${movie_overview}</p>
        </div>
    </div>`;
      $("#rightBox").append(temp_html);
    });
  },
});
