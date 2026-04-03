<script lang="ts">
  import { browser } from "$app/environment";
  import { onMount } from "svelte";
  import * as THREE from "three";
  import {
    ArcballControls,
    EffectComposer,
    RenderPass,
    UnrealBloomPass,
  } from "three/examples/jsm/Addons.js";
  import { getBody, getMouseBall } from "$lib/utils/model-collision/get_bodies";
  import getLayer from "$lib/utils/model-collision/get_layer";
  import type { RigidBody } from "@dimforge/rapier3d";
  import { loadModel } from "$lib/utils/model-collision/model_collision";
  // import { loadModel } from "$lib/utils/model_test_rapier";

  let { data } = $props();

  let isSound: boolean = true;
  let volume: number = 0.4; // 0.5 = half

  // Basic
  let container: Element | HTMLElement;
  let scene: THREE.Scene;
  let camera: THREE.PerspectiveCamera;
  let renderer: THREE.WebGLRenderer;
  let controls: ArcballControls;
  let clock: THREE.Clock;

  let mouse: THREE.Vector2;

  // Sound
  let audioLoader: THREE.AudioLoader;
  let audioListener: THREE.AudioListener;
  let audio: THREE.Audio;

  function init() {
    container = document.getElementById("demo")!;
    // scene
    scene = new THREE.Scene();
    // camera
    const aspect = container.clientWidth / container.clientHeight;
    camera = new THREE.PerspectiveCamera(45, aspect, 0.1, 1000);
    scene.add(camera);
    // renderer
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    // renderer.shadowMap.enabled = true;
    // renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    container.appendChild(renderer.domElement);
    // controls
    controls = new ArcballControls(camera, renderer.domElement, scene);
    controls.update();
    // helpers
    scene.add(new THREE.GridHelper(3, 6)); // size, division
    // scene.add(new THREE.AxesHelper(2));
    const axesHelper = new THREE.AxesHelper(2);
    axesHelper.setColors("red", "green", "blue");
    axesHelper.position.set(-2, 0, -2);
    scene.add(axesHelper);
    // clock
    clock = new THREE.Clock();
    // mouse
    mouse = new THREE.Vector2();
    // audio
    audioLoader = new THREE.AudioLoader();
    audioListener = new THREE.AudioListener();
    audio = new THREE.Audio(audioListener);
  }

  if (browser) {
    onMount(async () => {
      init();
      camera.position.set(1, 2, 8);

      //* Your code here...
      //

      /*
      If your scene appears too bright or washed out,
      consider applying tone mapping to your WebGLRenderer
      (e.g., renderer.toneMapping = THREE.ACESFilmicToneMapping;).
      */
      renderer.toneMapping = THREE.ACESFilmicToneMapping;
      renderer.toneMappingExposure = 1.8;

      // ------------------------------------
      const RAPIER = await import("@dimforge/rapier3d");
      // const gravity = { x: 0.0, y: -9.81, z: 0.0 };
      const gravity = { x: 0.0, y: 0.0, z: 0.0 };
      const world = new RAPIER.World(gravity);

      // post-processing (optional) ---------
      const renderScene = new RenderPass(scene, camera);

      const bloomPass = new UnrealBloomPass(
        new THREE.Vector2(container.clientWidth, container.clientHeight),
        1.5,
        0,
        0.002
      );
      bloomPass.strength = 2.0;
      bloomPass.radius = 0;
      bloomPass.threshold = 0.005;

      const composer = new EffectComposer(renderer);
      composer.addPass(renderScene);
      composer.addPass(bloomPass);

      // ------------------------------------
      type typeBody = {
        mesh: THREE.Mesh<THREE.IcosahedronGeometry> | THREE.Object3D;
        rigid: RigidBody;
        update: () => void;
      };

      const bodies: typeBody[] = [];

      //!!!!!! HERE
      // const numBodies = 10;
      // for (let i = 0; i < numBodies; i++) {
      //   const body: typeBody = await loadModel(RAPIER, world, "sample.pdb");
      //   body.mesh.scale.set(0.5, 0.5, 0.5);
      //   bodies.push(body);
      //   scene.add(body.mesh);
      // }

      for (let i = 0; i < data.files.length; i++) {
        const body: typeBody = await loadModel(
          RAPIER,
          world,
          `/substructure/parallel/${data.subDir}/pdbs`,
          data.files[i]
        );
        body.mesh.scale.set(0.4, 0.4, 0.4);
        bodies.push(body);
        scene.add(body.mesh);
      }

      // ------------------------------------
      const mouseBall = getMouseBall(RAPIER, world);
      scene.add(mouseBall.mesh);

      // ------------------------------------
      const hemiLight = new THREE.HemisphereLight(0x00bbff, 0xaa00ff);
      hemiLight.intensity = 0.2;
      scene.add(hemiLight);

      // ------------------------------------
      // BG
      const sprites = getLayer({
        hue: 0.0,
        numSprites: 8,
        opacity: 0.2,
        radius: 10,
        size: 24,
        sat: 0.1,
        z: -10.5,
      });
      scene.add(sprites);

      // ------------------------------------
      // Audio
      if (isSound) {
        audioLoader.load("/audio/space-chords-loop-310493.mp3", (buffer) => {
          audio.setBuffer(buffer);
          audio.setLoop(true);
          audio.setVolume(volume);
          audio.play();
        });
      }

      //
      // renderer.setAnimationLoop(null);
      renderer.setAnimationLoop(() => {
        tick();
        // renderer.render(scene, camera); // Replace with composer.render(delta);
        controls.update();
      });

      function tick() {
        const delta = clock.getDelta();
        // cube.userData.update(delta);
        world.step();
        mouseBall.update(mouse);
        bodies.forEach((b: typeBody) => b.update());
        composer.render(delta);
      }
    });
  }
</script>

<svelte:window
  onresize={() => {
    camera.aspect = container.clientWidth / container.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
  }}
  onmousemove={(e: MouseEvent) => {
    const rect = renderer.domElement.getBoundingClientRect();
    mouse.x = ((e.clientX - rect.left) / window.innerWidth) * 2 - 1;
    mouse.y = -((e.clientY - rect.top) / window.innerHeight) * 2 + 1;
  }}
/>

<div id="demo" class="container-full">
  <!-- Reset button -->
  <button
    class="absolute w-full/2 top-2 btn btn-lg bg-white text-black"
    onclick={() => {
      setTimeout(() => {
        controls.reset();
        camera.position.set(1, 2, 8);
      }, 10);
    }}>Reset</button
  >
  <label for="" class="absolute left-10, top-18 text-4xl text-white"
    >{data.files.length} Molecule's Collision</label
  >
</div>
