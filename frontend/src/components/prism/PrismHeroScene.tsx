"use client";

import { Suspense, useMemo, useState } from "react";
import { Canvas } from "@react-three/fiber";
import { Environment, Float, MeshDistortMaterial, OrbitControls } from "@react-three/drei";
import { useReducedMotion } from "framer-motion";
import { Sparkles } from "lucide-react";
import { useNetworkAware } from "@/hooks/useNetworkAware";

function supportsWebGL() {
  if (typeof document === "undefined") return true;

  try {
    const canvas = document.createElement("canvas");
    return Boolean(
      canvas.getContext("webgl2") ||
      canvas.getContext("webgl") ||
      canvas.getContext("experimental-webgl"),
    );
  } catch {
    return false;
  }
}

function KnowledgeCluster({ reducedMotion }: { reducedMotion: boolean }) {
  const positions = useMemo(
    () => [
      [-1.9, 0.8, 0],
      [1.7, 1.1, -0.4],
      [-0.4, -1.4, -0.6],
      [2.1, -0.8, 0.8],
      [-2.2, -0.3, 0.4],
    ],
    [],
  );

  return (
    <group>
      <Float
        speed={reducedMotion ? 0 : 1.9}
        rotationIntensity={reducedMotion ? 0 : 0.6}
        floatIntensity={reducedMotion ? 0 : 0.9}
      >
        <mesh position={[0, 0, 0]}>
          <icosahedronGeometry args={[1.1, 1]} />
          <MeshDistortMaterial
            color="#93c5fd"
            distort={0.32}
            speed={reducedMotion ? 0 : 1.6}
            roughness={0.08}
            metalness={0.45}
            transparent
            opacity={0.92}
          />
        </mesh>
      </Float>

      {positions.map((position, index) => (
        <Float
          key={index}
          speed={reducedMotion ? 0 : 1.2 + index * 0.2}
          rotationIntensity={reducedMotion ? 0 : 0.4}
          floatIntensity={reducedMotion ? 0 : 0.8}
        >
          <mesh position={position as [number, number, number]}>
            <octahedronGeometry args={[0.26 + index * 0.05, 0]} />
            <meshStandardMaterial
              color={index % 2 === 0 ? "#67e8f9" : "#a78bfa"}
              emissive={index % 2 === 0 ? "#164e63" : "#312e81"}
              roughness={0.22}
              metalness={0.55}
            />
          </mesh>
        </Float>
      ))}
    </group>
  );
}

export function PrismHeroScene() {
  const reducedMotion = Boolean(useReducedMotion());
  const { isSlowConnection, effectiveType, saveData } = useNetworkAware();
  const [webglSupported] = useState(() => supportsWebGL());
  const canRenderInteractiveScene = webglSupported && !isSlowConnection;

  return (
    <div
      data-testid="prism-hero-scene"
      data-reduced-motion={reducedMotion ? "true" : "false"}
      data-webgl={webglSupported ? "canvas" : "fallback"}
      data-network={isSlowConnection ? effectiveType : "default"}
      className="relative h-[360px] w-full overflow-hidden rounded-[calc(var(--radius)*1.2)] border border-[var(--border)] bg-[radial-gradient(circle_at_top,_rgba(96,165,250,0.18),_transparent_46%),linear-gradient(180deg,rgba(12,18,34,0.9),rgba(7,12,24,0.96))] shadow-[var(--shadow-card)]"
    >
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_rgba(167,139,250,0.18),_transparent_55%)]" />
      {canRenderInteractiveScene ? (
        <Suspense fallback={<div className="absolute inset-0" />}>
          <Canvas camera={{ position: [0, 0, 5.8], fov: 42 }}>
            <color attach="background" args={["#08111f"]} />
            <ambientLight intensity={1.2} />
            <directionalLight position={[2, 4, 3]} intensity={2.5} color="#dbeafe" />
            <pointLight position={[-3, -2, 2]} intensity={1.8} color="#67e8f9" />
            <pointLight position={[3, 0, -1]} intensity={1.2} color="#a78bfa" />
            <KnowledgeCluster reducedMotion={reducedMotion} />
            <Environment preset="city" />
            <OrbitControls
              enableZoom={false}
              enablePan={false}
              autoRotate={!reducedMotion}
              autoRotateSpeed={0.8}
              maxPolarAngle={Math.PI / 1.8}
              minPolarAngle={Math.PI / 2.3}
            />
          </Canvas>
        </Suspense>
      ) : (
        <div
          data-testid="prism-hero-fallback"
          className="absolute inset-0 flex flex-col justify-between p-6"
        >
          <div className="flex items-center gap-2 text-[11px] font-bold uppercase tracking-[0.26em] text-[var(--text-muted)]">
            <Sparkles className="h-4 w-4 text-[var(--accent-cyan)]" />
            {webglSupported ? "Reduced Network Mode" : "Selective 3D Fallback"}
          </div>
          <div className="max-w-sm space-y-3">
            <h3 className="prism-title text-2xl font-bold text-[var(--text-primary)]">
              {webglSupported
                ? "The landing hero scales down cleanly on slower connections."
                : "The immersive hero still holds its place without WebGL."}
            </h3>
            <p className="text-sm leading-7 text-[var(--text-secondary)]">
              {webglSupported
                ? `Heavy scene work stays disabled on ${effectiveType}${saveData ? " with data saver" : ""}, while layout and messaging remain intact.`
                : "Layout, messaging, and product framing stay intact while the scene falls back to a static depth composition."}
            </p>
          </div>
          <div className="grid gap-3 sm:grid-cols-3">
            {["Curriculum-grounded AI", "Role-aware workflows", "Operational clarity"].map((label, index) => (
              <div
                key={label}
                className="rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.04)] p-4 backdrop-blur-sm"
                style={{ transform: `translateY(${index % 2 === 0 ? 0 : 8}px)` }}
              >
                <div className="mb-3 h-2 w-16 rounded-full bg-[linear-gradient(135deg,rgba(96,165,250,0.22),rgba(167,139,250,0.12))]" />
                <p className="text-sm font-semibold text-[var(--text-primary)]">{label}</p>
              </div>
            ))}
          </div>
        </div>
      )}
      <div className="pointer-events-none absolute inset-x-0 bottom-0 h-24 bg-gradient-to-t from-[rgba(8,17,31,0.95)] to-transparent" />
    </div>
  );
}
