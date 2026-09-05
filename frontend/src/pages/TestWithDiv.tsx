import { Card, CardContent } from '../components/ui';

export function TestWithDiv() {
  return (
    <Card>
      <CardContent>
        <div className="space-y-6">
          <div>Test 1</div>
          <div>Test 2</div>
          <div>Test 3</div>
          <div>Test 4</div>
          <div>Test 5</div>
          <div>Test 6</div>
          <div>Test 7</div>
          <div>Test 8</div>
          <div>Test 9</div>
          <div>Test 10</div>
        </div>
      </CardContent>
    </Card>
  );
}