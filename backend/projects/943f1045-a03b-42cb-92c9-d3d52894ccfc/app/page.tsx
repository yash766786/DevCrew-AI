import React, { useState } from 'react';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import HeroSection from '@/components/HeroSection';
import ProjectCard from '@/components/ProjectCard';
import ProjectDetail from '@/components/ProjectDetail';
import ContactForm from '@/components/ContactForm';
import SkillBadge from '@/components/SkillBadge';
import SocialLinks from '@/components/SocialLinks';

const projects = [
  { id: 1, title: 'Project One', description: 'A brief description of project one.', image: '/images/project1.jpg' },
  { id: 2, title: 'Project Two', description: 'A brief description of project two.', image: '/images/project2.jpg' },
  { id: 3, title: 'Project Three', description: 'A brief description of project three.', image: '/images/project3.jpg' },
];

const skills = ['JavaScript', 'TypeScript', 'React', 'Next.js', 'Tailwind CSS', 'Node.js'];

export default function Home() {
  const [selectedProject, setSelectedProject] = useState(projects[0]);

  return (
    <div className="min-h-screen flex flex-col bg-gray-50 text-gray-900">
      <Navbar />
      <main className="flex-1">
        {/* Home Section */}
        <section id="home" className="py-20 bg-white">
          <div className="container mx-auto px-4">
            <HeroSection />
            <h2 className="text-3xl font-semibold text-center mt-12 mb-6">Featured Projects</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {projects.map((project) => (
                <ProjectCard
                  key={project.id}
                  title={project.title}
                  description={project.description}
                  image={project.image}
                  onClick={() => setSelectedProject(project)}
                />
              ))}
            </div>
          </div>
        </section>

        {/* About Section */}
        <section id="about" className="py-20 bg-gray-100">
          <div className="container mx-auto px-4">
            <h2 className="text-3xl font-semibold text-center mb-6">About Me</h2>
            <div className="md:flex md:space-x-12">
              <div className="md:w-1/2">
                <h3 className="text-2xl font-medium mb-4">Biography</h3>
                <p className="mb-4">
                  I am a passionate developer with a love for building clean and efficient web applications.
                  With a background in computer science and years of experience in full-stack development,
                  I enjoy turning complex problems into simple, beautiful solutions.
                </p>
                <p>
                  My journey started with learning JavaScript in high school, and since then I have
                  continuously expanded my skill set to include modern frameworks and tools.
                </p>
              </div>
              <div className="md:w-1/2 mt-8 md:mt-0">
                <h3 className="text-2xl font-medium mb-4">Skills</h3>
                <div className="flex flex-wrap gap-3">
                  {skills.map((skill) => (
                    <SkillBadge key={skill} label={skill} />
                  ))}
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Projects Section */}
        <section id="projects" className="py-20 bg-white">
          <div className="container mx-auto px-4">
            <h2 className="text-3xl font-semibold text-center mb-6">Projects</h2>
            <h3 className="text-2xl font-medium mb-4">Project List</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {projects.map((project) => (
                <ProjectCard
                  key={project.id}
                  title={project.title}
                  description={project.description}
                  image={project.image}
                  onClick={() => setSelectedProject(project)}
                />
              ))}
            </div>
            <h3 className="text-2xl font-medium mt-12 mb-4">Project Details</h3>
            {selectedProject && (
              <ProjectDetail
                title={selectedProject.title}
                description={selectedProject.description}
                image={selectedProject.image}
              />
            )}
          </div>
        </section>

        {/* Contact Section */}
        <section id="contact" className="py-20 bg-gray-100">
          <div className="container mx-auto px-4">
            <h2 className="text-3xl font-semibold text-center mb-6">Contact Me</h2>
            <div className="md:flex md:space-x-12">
              <div className="md:w-1/2">
                <ContactForm />
              </div>
              <div className="md:w-1/2 mt-8 md:mt-0">
                <h3 className="text-2xl font-medium mb-4">Social Links</h3>
                <SocialLinks />
              </div>
            </div>
          </div>
        </section>
      </main>
      <Footer />
    </div>
  );
}