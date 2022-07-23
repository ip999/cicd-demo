import sum from './sum';

describe('Test sum function', function () {
  test('1 + 2 should equal 3', () => {
    expect(sum(1, 2)).toBe(3);
  });

  test('2 + 1 should equal 3', () => {
    expect(sum(2, 1)).toBe(3);
  });

  test('100 + 99 should equal 199', () => {
    expect(sum(100, 99)).toBe(199);
  });

});