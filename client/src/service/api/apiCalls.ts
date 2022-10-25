import axios from "axios";
import { SetStateAction } from "react";

const instance = axios.create({
    baseURL: 'http://localhost:5001/',
    headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Methods": "GET,HEAD,OPTIONS,POST,PUT",
        "Access-Control-Allow-Headers": "*"
    }
});


interface interfaceLocations {
    setLoading: (value: boolean) => void,
    setError: (value: boolean) => void,
    setSuccess: (value: boolean) => void,
    setResponse: (value: string[]) => void

}


export const getLocations = async (setLoading: { (value: SetStateAction<boolean>): void; (arg0: boolean): void; }, setError: { (value: SetStateAction<boolean>): void; (arg0: boolean): void; }, setSuccess: { (value: SetStateAction<boolean>): void; (arg0: boolean): void; }, setResponse: { (value: SetStateAction<string[]>): void; (arg0: any): void; }) => {
  setError(false);
  setLoading(true);
  instance.get('locations',)
  .then(function (response) {

      setLoading(false);
      setSuccess(true);
      setResponse(response.data.locations);

  })
  .catch(function (error) {

    setLoading(false);
    setError(true);
    console.log(error);
  })

}


export const postPath = async  ( setLoading:(value:boolean)=>void,setError:(value:boolean)=>void,
                             setSuccess:(value:boolean)=>void, setResponse:(data:any)=>void, postValues:any) => {
  setError(false);
  setLoading(true);
  instance.post('path',postValues)
  .then(function (response) {
    // handle success
      setLoading(false);
      setSuccess(true);
      setResponse(response.data.paths);  })
  .catch(function (error) {
    setLoading(false);
    setError(true);
    console.log(error);
  })




}