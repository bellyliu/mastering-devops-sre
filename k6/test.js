import http from 'k6/http';
import { sleep, check } from  'k6';

export const options = {
  stages: [
    { duration: '3m', target: 100 },
    { duration: '10m', target: 100 },
    { duration: '1m', target: 0}
  ]
};

export default function(){
    const params = {
        headers: {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
        },
    };
    let res = http.get('https://cerrapoints.in/', params);
    check(res, { "status is 200": (res) => res.status === 200 });
    sleep(1);
}