import test from 'node:test';
import assert from 'node:assert/strict';
import { validateTicketStatus } from '../src/domain/value-objects/TicketStatus.js';

test('validateTicketStatus accepts OPEN', () => {
  assert.equal(validateTicketStatus('OPEN'), 'OPEN');
});

test('validateTicketStatus rejects invalid values', () => {
  assert.throws(() => validateTicketStatus('DONE'));
});
