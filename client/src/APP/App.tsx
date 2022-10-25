import React, {useEffect, useState} from 'react';
import { Space, Spin, Typography, Select } from 'antd';

import './App.css';
import {Table, Row} from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { Button } from 'antd';
import "antd/dist/antd.css";
import { DatePicker } from 'antd';
import type { DatePickerProps } from 'antd/es/date-picker';
import {getLocations, postPath} from "../service/api/apiCalls";




interface travelPath {
  "arrival": string,
  "departure": string,
  "name": string
}

interface travelType {
  "PAID": string,
  "TRID": string,
  "path": travelPath[]

}

const columns: ColumnsType<travelPath> = [
  {
    title: 'Prichod',
    dataIndex: 'arrival',
    key: 'arrival',
  },
  {
    title: 'Odchod',
    dataIndex: 'departure',
    key: 'departure',
  },
  {
    title: 'Stanice',
    dataIndex: 'name',
    key: 'name',
  },
];




function App() {
  // sets the destination and departure location
  const { Text } = Typography;
  const { Option } = Select;

  // ---- first load for trains
  const [stations,setStations] = useState<string[]>([]);
  const [loadingPage, setLoadingPage] = useState<boolean>(false);
  const [errorPage,setErrorPage] = useState<boolean>(false);
  const [succesPage, setSuccesPage] = useState<boolean>(false);
  // ---- first load for trains

  // ---- result of search
  const [paths,setPaths] = useState<travelType[]>([]);
  const [loadingPaths, setLoadingPaths] = useState<boolean>(false);
  const [errorPaths,setErrorPaths] = useState<boolean>(false);
  const [succesPaths, setSuccesPaths] = useState<boolean>(false);
  // ---- result of search

  const [from,setFrom] = useState<string|undefined>(undefined);
  const [to,setTo] = useState<string|undefined>(undefined);
  const [date,setDate]= useState<string|undefined>(undefined);


  const [errorForm, setErrorForm] = useState<boolean>(false);


  const onChangeFrom = (value: string) => {
    setFrom(value);
    console.log(`selected ${value}`);
  };

  const onChangeTo = (value: string) => {
    setTo(value);
    console.log(`selected ${value}`);
  };




  const onDatepickerChange = (
    value: DatePickerProps['value'],
    dateString: string,
  ) => {
   setDate( dateString );
   console.log(dateString);
  };




 const sendFilterRequest = () => {

    if ( from !== undefined && to !== undefined && date !== undefined){
      setErrorForm(false);
        const postData = {
          date,
          from,
          to
        }
        const json = JSON.stringify(postData);

        postPath(setLoadingPaths,setErrorPaths,setSuccesPaths,setPaths,json)
    }
    else{
      setErrorForm(true);
      console.log({from,to,date})
    }


  };

  useEffect(()=>{

    getLocations(setLoadingPage,setErrorPage,setSuccesPage,setStations);

  },[])

  useEffect(()=> {console.log(paths)},[paths])


  return (
      <div className="App">
      {loadingPage && (
          <Space size="middle">
            <Spin size="large" />
            </Space>)}

      {errorPage && (
          <Space size="middle">
            <Text type="danger">Chyba na pripojeni servera</Text>
          </Space>
      )}
        {succesPage && (
            <div>
              <div className='InputsContainer'>
                <Row>
                <Space>
                  <Select
                        showSearch
                        style={{
                          width: "350px"
                        }}
                        placeholder="Zadajte východziu stanicu"
                        optionFilterProp="children"
                        onChange={onChangeFrom}
                        filterOption={(input, option) =>
                          (option!.children as unknown as string).toLowerCase().includes(input.toLowerCase())
                        }
                      >
                      {stations.map((value)=> <Option value={value}>{value}</Option>)}
                  </Select>
                    </Space>
                </Row>
                <Row>
                <Space>

                  <Select
                    showSearch
                                            style={{
                          width: "350px"
                        }}
                    placeholder="Zadajte odchodziu stanicu"
                    optionFilterProp="children"
                    onChange={onChangeTo}
                    filterOption={(input, option) =>
                      (option!.children as unknown as string).toLowerCase().includes(input.toLowerCase())
                    }
                  >
                    {stations.map((value)=> <Option value={value}>{value}</Option>)}
                  </Select>
                </Space>
                </Row>
              <Row>
              <div className='DatepickerContainer'>
                <DatePicker showTime onChange={onDatepickerChange} name='datum'/>
              </div>
              </Row>
              <Row>
              <div className='buttonContainer'>
                <Button onClick={sendFilterRequest} type="primary">Odoslať</Button>
              </div>
              </Row>
              </div>

              <div>
                  {errorForm && (
                              <Text type="danger">Zadajte vsetky informacie</Text>
                  )}

                  {!errorForm && loadingPaths && !errorPaths && (
                                <Space size="middle">
                                  <Spin size="large" />
                               </Space>
                  )}
                  {!errorForm && !errorPaths&& !loadingPaths && succesPaths && paths.length>0 && (

                          paths.map((value) =>
                          <div>
                            <Text>Trid value {value.TRID}</Text>
                            <Table columns={columns} dataSource={value.path}/>
                          </div>

                      ))}

                  {!errorForm && !loadingPaths && succesPaths && paths.length  === 0 && (
                      <Text type="danger">Bolo najdenych 0 spojov</Text>
                  )}

              </div>
            </div>


        )}
      </div>
  )

}

export default App;

//