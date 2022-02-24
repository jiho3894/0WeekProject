$(".navbar_userMenu").click(() => {
  $(".detailBox").slideToggle(100);
});

const favorite = () => {
  alert("즐겨찾기 완료를 눌러봤습니다");
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
    });
  },
});
