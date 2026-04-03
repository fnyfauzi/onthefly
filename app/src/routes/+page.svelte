<script lang="ts">
  import { browser } from "$app/environment";
  import { onMount } from "svelte";
  import * as THREE from "three";

  // import { ArcballControls, CSS2DRenderer } from "three/examples/jsm/Addons.js";

  import { loadModel } from "$lib/utils/model_cubemap_cover.js";

  let model: THREE.Mesh;
  const isRealistic: boolean = true;

  // Basic
  let container: Element | HTMLElement;
  let scene: THREE.Scene;
  let camera: THREE.PerspectiveCamera;
  let renderer: THREE.WebGLRenderer;
  // let labelRenderer: CSS2DRenderer;
  // let controls: ArcballControls;
  let clock: THREE.Clock;

  function init() {
    container = document.getElementById("demo")!;
    // scene
    scene = new THREE.Scene();
    // camera
    const aspect = container.clientWidth / container.clientHeight;
    camera = new THREE.PerspectiveCamera(45, aspect, 0.1, 1000);
    scene.add(camera);
    // renderer
    // renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer = new THREE.WebGLRenderer();
    renderer.setSize(container.clientWidth, container.clientHeight, false);
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    // renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    container.appendChild(renderer.domElement);
    // label renderer
    // labelRenderer = new CSS2DRenderer();
    // labelRenderer.setSize(container.clientWidth, container.clientHeight);
    // labelRenderer.domElement.style.position = "absolute";
    // labelRenderer.domElement.style.top = "0px";
    // labelRenderer.domElement.style.pointerEvents = "none";
    // container.appendChild(labelRenderer.domElement);
    // controls
    // controls = new ArcballControls(camera, renderer.domElement, scene);
    // controls.update();
    // clock
    clock = new THREE.Clock();
  }

  if (browser) {
    onMount(async () => {
      init();
      // camera.position.set(1, 1, 5);
      camera.position.set(0, 0, 5);

      renderer.toneMapping = THREE.ACESFilmicToneMapping;
      renderer.toneMappingExposure = 1.8;

      const mol1 = await new THREE.TextureLoader().loadAsync(
        "/textures/gettyimages-1909960292-2048x2048.jpg"
      );
      mol1.mapping = THREE.EquirectangularReflectionMapping;
      mol1.colorSpace = THREE.SRGBColorSpace;

      // --------------------------
      const createModel = async function (
        texture: THREE.DataTexture | THREE.CubeTexture | THREE.Texture,
        envMapType:
          | typeof THREE.EquirectangularReflectionMapping
          | typeof THREE.CubeReflectionMapping
      ) {
        model = (await loadModel(
          texture,
          envMapType,
          isRealistic
          // document,
          // container
        )) as THREE.Mesh;
        model.name = "model";
        scene.add(model);
        model.scale.set(0.5, 0.5, 0.5);
      };
      await createModel(mol1, THREE.EquirectangularReflectionMapping); // Initial, default
      scene.background = mol1; // Initial, default
      if (isRealistic) scene.environment = mol1;

      let delta = 0;
      let interval = 1 / 30;

      renderer.setAnimationLoop((time: number) => {
        delta += clock.getDelta();
        if (delta > interval) {
          tick(time);
          renderer.render(scene, camera);
          // labelRenderer.render(scene, camera);
          // controls.update();
          delta = delta % interval;

          // camera.position.x = camera.position.x * Math.cos(0.1) - camera.position.x * Math.sin(0.1);
          model.rotation.x += delta;
        }
      });

      function tick(time: number) {
        // const delta = clock.getDelta();
        // cube.userData.update(delta);
        // model.userData.update();
        // model.rotation.x = time / 1000;
        // model.rotation.y = time / 1000;
      }
    });
  }
</script>

<svelte:window
  onresize={() => {
    camera.aspect = container.clientWidth / container.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.clientWidth, container.clientHeight);
    // labelRenderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
  }}
  onmousemove={(e: MouseEvent) => {
    // const rect = renderer.domElement.getBoundingClientRect();
    // mouse.x = ((e.clientX - rect.left) / window.innerWidth) * 2 - 1;
    // mouse.y = -((e.clientY - rect.top) / window.innerHeight) * 2 + 1;
  }}
/>

<div id="demo" class="container-full">
  <div
    class="absolute flex flex-col h-screen w-full justify-center items-center"
  >
    <!-- Top  -->
    <div
      class="flex border border-[rgba(255,255,255,255)] p-4 rounded-2xl w-1/2 h-1/2 justify-around items-center"
    >
      <!-- Left -->
      <div
        class="flex flex-col items-center space-y-4 rounded-xl p-10 bg-[rgba(196,74,137,0.8)]"
      >
        <div class="flex items-center space-x-2">
          <!-- class="animate-spin" -->
          <img src="/images/viewer.png" alt="" width="80" />
          <span class="text-4xl text-white">ArtSMol</span>
        </div>
        <div class="text-xl text-white">Artivila Small Molecule</div>
      </div>
      <!-- Right -->
      <div
        class="flex flex-col rounded-full items-center p-20 bg-[rgba(196,74,137,0.8)]"
      >
        <div class="text-xl text-white">What is ArtSMol ?</div>
        <div class="text-lg mt-4">
          <div class="text-lg text-white">1. Small molecule processing.</div>
          <div class="text-lg text-white">2. 3D viewer animation.</div>
          <div class="text-lg text-white">3. Writlen on typescript.</div>
          <div class="text-lg text-white">4. Fast execution.</div>
          <div class="text-lg text-white">5. Internal office usage.</div>
        </div>
        <div class="mt-8 flex justify-center">
          <!-- <a href="/protected" class="link text-5xl text-[rgba(196,74,137,0.8)]">Try it Now!</a> -->
          <a href="/protected" class="link text-5xl text-yellow-500 font-bold"
            >Try it Now!</a
          >
        </div>
      </div>
    </div>
  </div>
</div>
