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
  const starColor = favorite.querySelector(".favor-btn").style.color;
  starColor === "red"
    ? alert("이미 즐겨찾기한 항목입니다")
    : $.ajax({
        type: "POST",
        url: "/manage_star",
        data: {
          movie_id_give: id,
          movie_title_give: title,
          poster_path_give: poster,
          movie_overview_give: overview,
          oder_flag_give: "add",
        },
        success: (response) => {
          alert(response.msg);
          location.reload();
        },
      });
};

$.ajax({
  type: "GET",
  url: "https://api.themoviedb.org/3/movie/popular?api_key=9594c9ccbbcc42235a2072ad7d3699ae&language=ko-KR&page=1",
  success: (response) => {
    const movies = response.results;
    movies.slice(0, 20).map((data, index) => {
      const movie_id = data.id;
      const image_path = data.backdrop_path;
      const movie_title = data.title;
      const movie_desc = data.overview;
      let temp_html = `<div  class="favorite">
                              <div class="slid_movie" style="background-image: url('https://image.tmdb.org/t/p/original/${image_path}')"/>
                              <div class="movie_desc">
                                  <p class="movie_id">${movie_id}</p>
                                  <div class="titleBox">
                                    <p class="movie-title">${movie_title}</p>
                                    <button onclick="favorite(${index})" class="favor-btn"><p>★</p></button></div>
                                  <p class="movie-desc-simple">${movie_desc}</p>
                              </div>/
                          </div>`;
      $(".movie_scroll_section").append(temp_html);
      $.ajax({
        type: "GET",
        url: "/star_load",
        success: (response) => {
          const row = index;
          const test = $(".favorite")[row];
          const id = test.querySelector(".movie_id").innerHTML;
          const array_movie = [];
          response.favorites_list.map((data) => {
            array_movie.push(data.movie_id);
          });
          array_movie.findIndex((movie) =>
            movie === id
              ? test
                  .querySelector(".favor-btn")
                  .setAttribute("style", "color: red;")
              : null
          );
        },
      });
    });
  },
});
$.ajax({
  type: "GET",
  url: "https://api.themoviedb.org/3/movie/now_playing?api_key=9594c9ccbbcc42235a2072ad7d3699ae&language=en-US&page=1",
  success: (response) => {
    const row = response.results;
    row.slice(0, 8).map((data, index) => {
      const poster = data.backdrop_path;
      let temp_html = `<div class="sliderBox ${index}" style="background-image: url('https://image.tmdb.org/t/p/original/${poster}')"></div>`;
      $(".sliderContainer").append(temp_html);
    });
    $(".sliderContainer").slick({
      slidesToShow: 1,
      slidesToScroll: 1,
      autoplay: true,
      autoplaySpeed: 5000,
    });
  },
});
