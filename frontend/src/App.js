import { apiKey } from './config.js';
import { useState, useEffect } from 'react';
import GetMovie from './Components/GetMovie';

function App() {
  const [showWelcome, setShowWelcome] = useState(true)
  const [showMovieSearch, setShowMovieSearch] = useState(false)
  const [submit, setSubmit] = useState(false)
  const [submitCount, setSubmitCount] = useState(0)
  const [movies, addMovie] = useState([])
  const [showLoading, setShowLoading] = useState(false)
  const [showResults, setShowResults] = useState(false)
  const [recs, setRecs] = useState([])

  //loading page
  useEffect(() => {
    if (submitCount === 2 && recs.length === 0) {
      Loading();
    }
  }, [submitCount]);

  //when "click to get started" button is clicked
  function onClick() {
    setShowMovieSearch(true)
    setShowWelcome(false)
  }

  //keep track of number of movies submitted
  function updateSubmit(data) {
    setSubmitCount(submitCount + 1)
    setSubmit(true)
    setShowMovieSearch(true)
    addMovie([...movies, data])

  }

  //when movies submitted, recommendations from backend
  async function Loading() {
    setShowLoading(true)
    setSubmit(false)
    setShowMovieSearch(false)

    let movieArray = movies.map(movie => movie.movieid);
    const response = await fetch("http://127.0.0.1:5000/api/analyze-movies", {
      method: "POST",
      headers: {
        "Accept": "application/json",
        "Content-Type": "application/json"
      },
      body: JSON.stringify(movieArray)
    });
    
    if (response.ok) {
      
      const results = await response.json()
      for(let i in results){
        let movieid = results[i][0][1]
        let information = await getSynopsisandImage(movieid)
        results[i].push(...information)
      }
      setShowLoading(false)
      setShowResults(true)
      setRecs(results)
    }
  }

  //get synopsis and poster path for a movie
  async function getSynopsisandImage(movieId) {
    const response = await fetch(`https://api.themoviedb.org/3/movie/${movieId}language=en-US`, {
      headers: {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": `Bearer ${apiKey}`,
      },
    })
    if (response.ok) {
      const data = await response.json()
      return [data.overview, data.poster_path]
    }
    else return []
  }

  return (
    <div className="bg-light bg-opacity-50 container-fluid d-flex justify-content-center align-items-center vh-100">
      {(() => {
        //welcome page
        if (showWelcome) {
          return (
            <div className="row align-items-center">
              <button className="btn btn-primary" onClick={onClick}>click to get started</button>
            </div>
          )
        }

        //movie search page
        else if (showMovieSearch) {
          return (
            <GetMovie onResult={updateSubmit} movieNum={submitCount} />
          )
        }

        //glitch
        else if (submit && submitCount < 2) {
          return (
            <div>Something is wrong. Refresh and try again.</div>
          )
        }

        //loading page
        else if (showLoading && submitCount == 2) {
          return (
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
          )
        }
        //rec page
        else if (!showLoading && showResults) {
          return (
            <div class="justify-content-center col-8">
                <div id="captions" class="carousel slide">
                  <div class="carousel-indicators">
                  {recs.map((movie, index) => (
                    <button type="button" data-bs-target="#captions" data-bs-slide-to={index} className={`${index === 0 ? 'active':''}`} aria-current={`${index === 0 ? 'true':'false'}`}></button>
                  ))}
                    </div>
                  <div class="carousel-inner">
                  {recs.map((movie, index) => (
                    <>
                    <div class={`carousel-item ${index === 0 ? 'active' : ''}`}>
                      <img src={`https://image.tmdb.org/t/p/original${movie[3]}`} class="d-md-block w-100" alt={movie}/>
                      <h5>{movie[0][0]}</h5>
                      <p>{movie[2]}</p>
                    </div>
                      
                    </>
                    ))}
                  </div>
                  <button class="carousel-control-prev" type="button" data-bs-target="#captions" data-bs-slide="prev">
                    <span class="carousel-control-prev-icon" aria-hidden="true"></span>
                    <span class="visually-hidden">Previous</span>
                  </button>
                  <button class="carousel-control-next" type="button" data-bs-target="#captions" data-bs-slide="next">
                    <span class="carousel-control-next-icon" aria-hidden="true"></span>
                    <span class="visually-hidden">Next</span>
                  </button>
                </div>
              
            </div>
          )
        }
      })()}
    </div >
  );
}

export default App;
