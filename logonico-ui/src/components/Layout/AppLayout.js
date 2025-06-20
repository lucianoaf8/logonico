import React from 'react';
import Header from '../Header/Header';
import Sidebar from '../Sidebar/Sidebar';
import Gallery from '../Gallery/Gallery';
import SelectionPanel from '../SelectionPanel/SelectionPanel';
import ResizeHandle from '../Gallery/ResizeHandle'; // Fixed: Changed from ../common/ResizeHandle
import Footer from '../Footer/Footer';

export default function AppLayout({ onToggleTheme }) {
  return (
    <div className="container">
      <Header onToggleTheme={onToggleTheme}/>
      <Sidebar />
      <Gallery />
      <SelectionPanel />
      <ResizeHandle />
      <footer className="footer">{/* you can move Footer into its own component similarly */}</footer>
      <Footer />
    </div>
  );
}