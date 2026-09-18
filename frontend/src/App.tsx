import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Join } from "./pages/Join";
import { Status } from "./pages/Status";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Join />} />
        <Route path="/status/:token" element={<Status />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
