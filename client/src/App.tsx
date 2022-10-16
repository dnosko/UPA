import React from 'react';
import { Input } from 'antd';
import './App.css';
import {Table, Tag } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { Button } from 'antd';
import "antd/dist/antd.css";
import { DatePicker } from 'antd';
import type { DatePickerProps } from 'antd/es/date-picker';


interface DataType {
  odkud: string;
  kam: string;
  age: number;
  kdy_odjezd: string;
  kdy_prijezd: string;
  kraj: string;
  tags: string[];
}

// idk co chceme zobrazovat este, takže toto kludne všetko možme zeditovať
const columns: ColumnsType<DataType> = [
  {
    title: 'Odkud',
    dataIndex: 'odkud',
    key: 'odkud',
    render: text => <a href={"./"}>{text}</a>,
  },
  {
    title: 'Kam',
    dataIndex: 'kam',
    key: 'kam',
  },
  {
    title: 'Odjezd',
    dataIndex: 'kdy_odjezd',
    key: 'kdy_odjezd',
  },
  {
    title: 'Prijezd',
    dataIndex: 'kdy_prijezd',
    key: 'kdy_prijezd',
  },
  {
    title: 'Kraj',
    dataIndex: 'kraj',
    key: 'kraj',
  },
  {
    title: 'Tags',
    key: 'tags',
    dataIndex: 'tags',
    render: (_, { tags }) => (
      <>
        {tags.map(tag => {
          let color = tag.length > 5 ? 'geekblue' : 'green';
          if (tag === 'loser') {
            color = 'volcano';
          }
          return (
            <Tag color={color} key={tag}>
              {tag.toUpperCase()}
            </Tag>
          );
        })}
      </>
    ),
    }
];

const data: DataType[] = [
  {
    odkud: 'Jihlava',
    kam: 'John Brown',
    age: 32,
    kdy_odjezd: '09:00:00',
    kdy_prijezd: '09:32:00',
    kraj: 'Vysočina',
    tags: ['asik toto', 'zmažeme'],
  },
  {
    odkud: 'Brno',
    kam: 'Praha',
    age: 42,
    kdy_odjezd: '09:30:00',
    kdy_prijezd: '09:54:00',
    kraj: 'Jihočeský kraj',
    tags: ['loser'],
  },
  {
    odkud: 'Královec',
    kam: 'Ostrava',
    age: 32,
    kdy_odjezd: '10:00:00',
    kdy_prijezd: '10:44:00',
    kraj: 'Baník pyčo',
    tags: ['cool', 'teacher'],
  },
  {
    odkud: 'Královec',
    kam: 'Ostrava',
    age: 32,
    kdy_odjezd: '11:00:00',
    kdy_prijezd: '12:44:00',
    kraj: 'Jihomoravský',
    tags: ['fuckoff', 'bitch'],
  },
];


function App() {
  // sets the destination and departure location 
  const [formInputData, setFormInputData] = React.useState({
    odkud: '',
    kam: '',
  })

  // sets the date to be searched in the time tables
  const [formDateData, setFormDateData] = React.useState({
    datum: '',
  })

  // when user types into text inputs, store the change
  const onInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormInputData({ ...formInputData, [e.target.name]: e.target.value })
    console.log('Odkud: ', formInputData.odkud)
    console.log('Kam: ',formInputData.kam)

  };

  // when user selects date, store the change
  const onDatepickerChange = (
    value: DatePickerProps['value'],
    dateString: string,
  ) => {
    setFormDateData({ datum : dateString })
    console.log('Formatted Selected Time: ', formDateData.datum);
  };

  const sendFilterRequest = () => {
    console.log('Send request to backend!');
  };


  return (
    <div className="App">
      <div className='InputsContainer'>
        <Input className='Input' name='odkud' placeholder="Zadajte východziu stanicu" allowClear onChange={onInputChange} />
        <Input className='Input' name='kam' placeholder="Zadajte cielovu stanicu" allowClear onChange={onInputChange} />
      </div>
      <div className='DatepickerContainer'>
        <DatePicker showTime onChange={onDatepickerChange} name='datum'/>
      </div>
      <div className='buttonContainer'>
        <Button onClick={sendFilterRequest} type="primary">Odoslať</Button>
      </div>
      <div>
        <Table columns={columns} dataSource={data} />
      </div>
    </div>
  );
}

export default App;
