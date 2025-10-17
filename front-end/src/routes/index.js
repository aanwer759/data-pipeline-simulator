
import React from 'react';
import { Route } from 'react-router-dom';

import Welcome from '../pages/Welcome';

export default function Routes() {
  return (
    <Route>
      <Route path="/" component={Welcome} />
    </Route>
  );
}
