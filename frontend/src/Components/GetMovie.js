import { useState } from 'react'

// autocomplete search bar function //

function GetMovie({ onResult, movieNum }) {
  const [activeSuggestionInd, setIndex] = useState(0);
  const [filteredSuggestions, setFilteredSuggesetions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [userInput, setUserInput] = useState("");
  const [movieId, setMovieId] = useState(0);
  const [posterpath, setPosterPath] = useState("");
  const [showImage, setShowImage] = useState(false);
  const [showMovie, setShowMovie] = useState(false);


  async function onChange(e) {
    setUserInput(e.currentTarget.value);

    const suggestions = filteredSuggestions;

    const response = await fetch(`https://api.themoviedb.org/3/search/movie?api_key=21b421ab2e0fb3417ba507e17c1d21df&query=${userInput}&include_adult=false&language=en-US`)
    const data = await response.json()
    for (const result of data["results"]) {
      let found = suggestions.some(movie => movie.id == result["id"])
      if (!found) suggestions.push({ title: result["title"], date: ` (${result["release_date"].slice(0, 4)})`, id: result["id"], poster: result["poster_path"] })
    }

    const filtered = suggestions.filter(
      suggestion =>
        suggestion.title.toLowerCase().indexOf(userInput.toLowerCase()) > -1
    );

    setIndex(0);
    setFilteredSuggesetions(filtered);
    setShowSuggestions(true);
  }

  function onSelectMovie(e) {
    setMovieId(filteredSuggestions[activeSuggestionInd].id);
    setPosterPath(filteredSuggestions[activeSuggestionInd].poster);
    setIndex(0)
    setFilteredSuggesetions([]);
    setShowSuggestions(false);
    setUserInput(e.currentTarget.innerText);
    setShowImage(true)
    return movieId
  }

  function onKeyDown(e) {
    if (e.keyCode === 13) {
      setMovieId(filteredSuggestions[activeSuggestionInd].id);
      setPosterPath(filteredSuggestions[activeSuggestionInd].poster);
      setIndex(0)
      setFilteredSuggesetions([]);
      setShowSuggestions(false);
      setUserInput(e.currentTarget.innerText);
      setShowImage(true)

      return movieId
    }
    else if (e.keyCode === 38) {
      if (activeSuggestionInd === 0) {
        return;
      }
      setIndex(activeSuggestionInd - 1)
    }
    else if (e.keyCode === 40) {
      if (activeSuggestionInd - 1 === filteredSuggestions.length) {
        return;
      }
      setIndex(activeSuggestionInd + 1)
    }

  }
  async function onSubmit(e) {
    const data = { title: userInput, movieid: movieId, poster: posterpath };

    await fetch("http://127.0.0.1:5000/api/post-movies", {
      method: "POST",
      headers: {
        "Accept": "application/json",
        "Content-Type": "application/json"
      },
      body: JSON.stringify(data)
    });
    onResult(data)
    setUserInput("")
    setShowImage(false)
    setShowMovie(false)

  }


  return (
<div className='col-9'>
  {!showImage ? (
    <div className="input-group">
      <div className='vstack gap-0' onKeyDown={onKeyDown}>
        <h1>Enter Movie #{movieNum + 1}</h1>
        <input
          className="form-control"
          onChange={onChange}
          value={userInput}
          movieid={movieId}
          posterpath={posterpath}
          aria-label={`Enter Movie ${movieNum + 1}`}
        />
        {userInput && filteredSuggestions.length < 1 && (
          <p>No suggestions. Try a different title. </p>
        )}
        {showSuggestions && userInput && (
          <ul className="list-group">
            {filteredSuggestions.slice(0, 5).map((suggestion, index) => (
              <li
                key={index}
                onMouseOver={() => setIndex(index)}
                className={`list-group-item list-group-item-action ${
                  activeSuggestionInd === index ? 'active' : ''
                }`}
                onClick={(e) => onSelectMovie(e)}
                aria-selected={activeSuggestionInd === index}
              >
                {`${suggestion.title} ${suggestion.date !== ' ()' ? suggestion.date : ''}`}
                <img
                  key={suggestion.id}
                  className="float-end"
                  width="40"
                  height="50"
                  src={`https://image.tmdb.org/t/p/original/${suggestion.poster}`}
                  alt={`Poster for ${suggestion.title}`}
                />
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  ) : (
    <div className='vstack gap-3 col-12'>
      <div className='row justify-content-center'>
        <h1 className='text-center'>Movie #{movieNum + 1}</h1>
      </div>
      <div className='row justify-content-center'>
        <img
          className="w-75 img-thumbnail"
          src={`https://image.tmdb.org/t/p/original/${posterpath}`}
          alt={`Poster for Movie ${movieNum + 1}`}
        />
      </div>
      <div className='row justify-content-center py-3'>
        <button className={`btn ${movieNum === 0 ? 'btn-primary' : 'btn-success'}`} onClick={onSubmit}>
          {movieNum === 0 ? 'Continue' : 'Get Movie Match'}
        </button>
      </div>
    </div>
  )}
</div>

  )
}

export default GetMovie
