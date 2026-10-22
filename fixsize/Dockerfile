```javascript
const CLOUD_RUN_URL =
  'https://YOUR-CLOUD-RUN-URL.run.app';

function doGet() {
  return HtmlService
    .createHtmlOutputFromFile('index')
    .setTitle('고정 길이 큐 시뮬레이터');
}

function callQueueApi(action, value) {

  const payload = {
    action: action
  };

  if (value !== undefined && value !== null && value !== '') {
    const numberValue = Number(value);

    if (!Number.isFinite(numberValue)) {
      throw new Error('숫자를 입력하세요.');
    }

    payload.value = numberValue;
  }

  const response = UrlFetchApp.fetch(
    CLOUD_RUN_URL + '/api/queue',
    {
      method: 'post',
      contentType: 'application/json',
      payload: JSON.stringify(payload),
      muteHttpExceptions: true
    }
  );

  const statusCode = response.getResponseCode();
  const responseText = response.getContentText();

  let data;

  try {
    data = JSON.parse(responseText);
  } catch (error) {
    throw new Error(
      '서버 응답을 확인할 수 없습니다: ' + responseText
    );
  }

  if (statusCode < 200 ||
      statusCode >= 300 ||
      data.ok !== true) {

    throw new Error(
      data.error || 'Cloud Run 요청에 실패했습니다.'
    );
  }

  return data;
}
```
