import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Host } from "./pages/Host";
import { Join } from "./pages/Join";
import { Status } from "./pages/Status";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Join />} />
        <Route path="/status/:token" element={<Status />} />
        <Route path="/host" element={<Host />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
