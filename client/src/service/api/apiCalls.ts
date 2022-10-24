import axios from "axios";

const instance = axios.create({
  baseURL: 'http://localhost:5001/',
  timeout: 1000,
  headers: {'X-Custom-Header': 'foobar'}
});




const getLocations = async ( setLoading:(value:boolean)=>void,setError:(value:boolean)=>void,
                             setSuccess:(value:boolean)=>void, setResponse:(data:any)=>void) => {
  setError(false);
  setLoading(true);
  instance.get('location',)
  .then(function (response) {

      setLoading(false);
      setSuccess(true);
      setResponse(response.data);

  })
  .catch(function (error) {

    setLoading(false);
    setError(true);
    console.log(error);
  })

}


const postPath = async  ( setLoading:(value:boolean)=>void,setError:(value:boolean)=>void,
                             setSuccess:(value:boolean)=>void, setResponse:(data:any)=>void, postValues:any) => {
  setError(false);
  setLoading(true);
  instance.post('travel',postValues)
  .then(function (response) {
    // handle success
      setLoading(false);
      setSuccess(true);
      setResponse(response.data);  })
  .catch(function (error) {
    setLoading(false);
    setError(true);
    console.log(error);
  })




}