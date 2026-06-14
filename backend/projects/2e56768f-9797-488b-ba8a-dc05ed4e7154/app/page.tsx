import { useState } from 'react';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import HeroSection from '@/components/HeroSection';
import ProjectGrid from '@/components/ProjectGrid';
import ProjectModal from '@/components/ProjectModal';
import DownloadButton from '@/components/DownloadButton';
import FilterButtons from '@/components/FilterButtons';

export default function Home() {
  const [selectedProject, setSelectedProject] = useState<any>(null);
  const [showModal, setShowModal] = useState(false);

  const handleProjectClick = (project: any) => {
    setSelectedProject(project);
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setSelectedProject(null);
  };

  return (
    <>
      <Navbar />
      <main className="container mx-auto px-4 py-8">
        <section id="hero" className="mb-12">
          <HeroSection />
        </section>

        <section id="intro" className="mb-12">
          <h2 className="text-3xl font-bold mb-4">About Me</h2>
          <p className="text-gray-700">
            I’m a passionate developer building clean and efficient web experiences. With a focus on modern technologies and user-centric design, I turn ideas into functional, beautiful products.
          </p>
        </section>

        <section id="featured-projects" className="mb-12">
          <h2 className="text-3xl font-bold mb-4">Featured Projects</h2>
          <FilterButtons />
          <ProjectGrid onProjectClick={handleProjectClick} />
        </section>

        <section id="cta" className="text-center mb-12">
          <h2 className="text-3xl font-bold mb-4">Let’s Work Together</h2>
          <DownloadButton text="Download Resume" />
        </section>
      </main>

      <Footer />

      {showModal && selectedProject && (
        <ProjectModal project={selectedProject} onClose={closeModal} />
      )}
    </>
  );
}