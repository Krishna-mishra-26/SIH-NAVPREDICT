import React, { useEffect, useRef } from 'react';

export const SatelliteOrbit = () => {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    const centerX = width / 2;
    const centerY = height / 2;

    let time = 0;

    const animate = () => {
      // Clear canvas
      ctx.fillStyle = '#0a1428';
      ctx.fillRect(0, 0, width, height);

      // Draw stars
      ctx.fillStyle = '#ffffff';
      for (let i = 0; i < 100; i++) {
        const x = Math.sin(i * 12.9898) * width;
        const y = Math.cos(i * 78.233) * height;
        ctx.fillRect(x % width, y % height, 1, 1);
      }

      // Draw Earth
      ctx.fillStyle = '#4b90e2';
      ctx.beginPath();
      ctx.arc(centerX, centerY, 40, 0, Math.PI * 2);
      ctx.fill();

      // Draw continent-like shapes
      ctx.fillStyle = '#2ecc71';
      ctx.fillRect(centerX - 20, centerY - 10, 15, 8);
      ctx.fillRect(centerX + 10, centerY, 12, 10);

      // Draw orbits
      ctx.strokeStyle = 'rgba(0, 224, 255, 0.3)';
      ctx.lineWidth = 1;
      for (let r = 80; r <= 200; r += 60) {
        ctx.beginPath();
        ctx.arc(centerX, centerY, r, 0, Math.PI * 2);
        ctx.stroke();
      }

      // Draw satellites
      const satellites = [
        { name: 'GEO', radius: 80, color: '#00e0ff', offset: 0 },
        { name: 'MEO', radius: 140, color: '#ffd700', offset: Math.PI / 3 },
        { name: 'MEO', radius: 140, color: '#ffd700', offset: (Math.PI / 3) + Math.PI },
        { name: 'GSO', radius: 200, color: '#ff6b6b', offset: Math.PI / 2 },
      ];

      satellites.forEach((sat, idx) => {
        const angle = (time * (idx + 1) * 0.02 + sat.offset) % (Math.PI * 2);
        const x = centerX + Math.cos(angle) * sat.radius;
        const y = centerY + Math.sin(angle) * sat.radius;

        // Draw satellite
        ctx.fillStyle = sat.color;
        ctx.beginPath();
        ctx.arc(x, y, 6, 0, Math.PI * 2);
        ctx.fill();

        // Draw glow
        ctx.strokeStyle = `rgba(${sat.color === '#00e0ff' ? '0, 224, 255' : sat.color === '#ffd700' ? '255, 215, 0' : '255, 107, 107'}, 0.5)`;
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(x, y, 10, 0, Math.PI * 2);
        ctx.stroke();

        // Draw label
        ctx.fillStyle = sat.color;
        ctx.font = '10px Poppins';
        ctx.fillText(sat.name, x + 12, y - 8);
      });

      time += 1;
      requestAnimationFrame(animate);
    };

    animate();
  }, []);

  return <canvas ref={canvasRef} width={500} height={400} className="w-full" />;
};
