<script lang="ts">
  import { browser } from "$app/environment";
  import { onMount } from "svelte";
  import * as THREE from "three";
  import { ArcballControls, ImprovedNoise } from "three/examples/jsm/Addons.js";
  import getLayer from "./getLayer";

  // For this Logic
  const amount = 10;

  // optional
  let isSound: boolean = true;
  let volume: number = 0.4; // 0.5 = half
  let isPlay: boolean = $state(false);

  // Basic
  let container: Element | HTMLElement;
  let scene: THREE.Scene;
  let camera: THREE.PerspectiveCamera;
  let renderer: THREE.WebGLRenderer;
  // let directionalLight: THREE.DirectionalLight;
  let controls: ArcballControls;
  let clock: THREE.Clock;
  // let gui: GUI;

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
    // // directionalLight
    // directionalLight = new THREE.DirectionalLight("white", 10);
    // directionalLight.position.set(-0.8, 1.8, 2.7);
    // directionalLight.target.position.set(0, 0, 0);
    // // directionalLight.castShadow = true;
    // scene.add(directionalLight);
    // scene.add(new THREE.DirectionalLightHelper(directionalLight, 0.2));
    // controls
    controls = new ArcballControls(camera, renderer.domElement, scene);
    controls.update();
    // helpers
    scene.add(new THREE.GridHelper(3, 6)); // size, division
    // scene.add(new THREE.AxesHelper(2));
    const axesHelper = new THREE.AxesHelper(2);
    // axesHelper.setColors("red", "green", "blue");
    axesHelper.position.set(-2, 0, -2);
    scene.add(axesHelper);
    // clock
    clock = new THREE.Clock();
    // gui
    // gui = new GUI();
    // gui.close();
    // mouse
    mouse = new THREE.Vector2();
    // audio
    if (isSound) {
      audioLoader = new THREE.AudioLoader();
      audioListener = new THREE.AudioListener();
      audio = new THREE.Audio(audioListener);
    }
  }

  if (browser) {
    onMount(async () => {
      init();
      // camera.position.set(1, 2, 8);
      camera.position.set(1, 2, amount * 2);
      // camera.position.set(-3, 8, 2);

      //* Your code here...
      //

      /*
      If your scene appears too bright or washed out,
      consider applying tone mapping to your WebGLRenderer
      (e.g., renderer.toneMapping = THREE.ACESFilmicToneMapping;).
      */
      renderer.toneMapping = THREE.ACESFilmicToneMapping;
      renderer.toneMappingExposure = 1.8;

      //
      const size = 0.5;
      const geo = new THREE.BoxGeometry(size, size, size);
      // const geo = new THREE.SphereGeometry(size, size, size);
      const mat = new THREE.MeshStandardMaterial();

      const count = amount ** 3; // jumlah mesh = x, y, z
      const mesh = new THREE.InstancedMesh(geo, mat, count);
      scene.add(mesh);

      // add noise
      const noise = new ImprovedNoise(); // this new for me
      const nAmp = 0.1; // play with this
      const nScale = 3; // play with this
      let nz;

      // Draw
      const offset = (amount - 1) * 0.5;
      const dummy = new THREE.Object3D();
      const color = new THREE.Color(0x000000);

      //
      const metacube = new THREE.Group();
      metacube.add(mesh);
      scene.add(metacube);
      metacube.userData = {
        update: (t: number) => {
          let i = 0;
          for (let x = 0; x < amount; x++) {
            for (let y = 0; y < amount; y++) {
              for (let z = 0; z < amount; z++) {
                nz =
                  noise.noise(t + x * nAmp, t + y * nAmp, t + z * nAmp) *
                  nScale;

                // play without move position
                dummy.position.set(offset - x, offset - y, offset - z);
                // play with move position
                // dummy.position.set(
                //   offset - x + nz,
                //   offset - y + nz,
                //   offset - z + nz
                // );

                // play with color (blink)
                // dummy.scale.setScalar(nz);

                // set color
                color.setHSL(0.95 + nz * 0.1, 1.0, 0.2 + nz * 0.1);
                mesh.setColorAt(i, color);
                if (mesh.instanceColor) {
                  mesh.instanceColor.needsUpdate = true;
                }

                // rotate each mesh
                dummy.rotation.y =
                  Math.sin(x * 0.25 + t) +
                  Math.sin(y * 0.25 + t) +
                  Math.sin(z * 0.25 + t);
                dummy.rotation.z = dummy.rotation.y * 2;

                // update
                dummy.updateMatrix();
                mesh.setMatrixAt(i, dummy.matrix);
                i += 1;
              }
            }
          }
          mesh.instanceMatrix.needsUpdate = true;
        },
      };

      // ------------------------------------
      const hemiLight = new THREE.HemisphereLight(0xffffff, 0x444444);
      scene.add(hemiLight);

      // ------------------------------------
      // BG
      const sprites = getLayer({
        hue: 0.6,
        numSprites: 8,
        opacity: 0.1,
        radius: 10,
        size: 24,
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
          // audio.play();
        });
      }

      //
      // renderer.setAnimationLoop(null);
      renderer.setAnimationLoop((time = 0) => {
        tick(time);
        renderer.render(scene, camera);
        controls.update();
      });

      function tick(time: number) {
        // time += 0.001;
        // metacube.userData.update(time);
        // let delta = clock.getDelta();
        // metacube.userData.update(delta);
        let t = clock.getElapsedTime();
        t += 0.001; // play with this
        metacube.userData.update(t);
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
    class="absolute left-2 top-2 btn btn-md bg-white text-black"
    onclick={() => {
      setTimeout(() => {
        controls.reset();
        // camera.position.set(1, 2, 8);
        camera.position.set(1, 2, amount * 2);
      }, 10);
    }}>Reset</button
  >
  <!-- Start/Stop Play Sound button -->
  <button
    class="absolute left-24 top-2 btn btn-md bg-white text-black"
    onclick={() => {
      isPlay = !isPlay;
      if (isSound) {
        if (isPlay) {
          audio.play();
        } else {
          // audio.stop();
          audio.pause();
        }
      }
    }}>{isPlay ? "Stop" : "Play"} Music</button
  >
  <label for="" class="absolute left-10, top-6 text-4xl text-white"
    >Meta Cube</label
  >
</div>
