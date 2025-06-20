import React from 'react';
import Header from '../Header/Header';
import Sidebar from '../Sidebar/Sidebar';
import Gallery from '../Gallery/Gallery';
import SelectionPanel from '../SelectionPanel/SelectionPanel';
import Footer from '../Footer/Footer';

export default function AppLayout({ onToggleTheme }) {
  return (
    <div className="container">
      <Header onToggleTheme={onToggleTheme} />
      <Sidebar />
      <Gallery />
      <SelectionPanel />
      <Footer />
    </div>
  );
}