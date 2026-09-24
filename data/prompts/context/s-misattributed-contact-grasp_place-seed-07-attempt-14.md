## Search State

- **Seed**: 7
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | -0.0503 | 0.26 | ✅ accepted |
| 13 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | pose_tolerance | contact_detected | time_limit | pose_tolerance | 9 | -0.1364 | 0.25 | ✅ accepted |
| 12 | descend → insert → grasp → approach → align → retract | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.2211 | 0.19 | ❌ rejected |
| 11 | descend → insert → grasp → approach → align → retract | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.2211 | 0.19 | ❌ rejected |
| 10 | descend → insert → grasp → approach → align → retract | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.2211 | 0.19 | ❌ rejected |

**Proposal policy**: task_score is 0.26 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
- task_score stagnant: change coupled targets, parameters, terminations, phase types, controls, subtasks, or ordering when evidence shows they need to change together.
A HOLD wastes an iteration when task_score is below 0.9.

## Optimisation Objective

Your goal is to **maximise task_score first, then composite score Q**:

> **Primary objective: task_score** — the fraction of episodes where the robot successfully completes the task. This is the most important metric. **Never propose a simpler or shorter skill if it reduces task_score.**

> **Q = fitness_score + termination_fidelity − complexity_penalty**

- `fitness_score`: shaped task reward (includes phase progress for contact-rich tasks)
- `termination_fidelity`: fraction of phases that terminated by designed condition (not timeout)
- `complexity_penalty`: cost for over-parameterised or over-phased designs

**Warning**: Do not reduce phases or parameters to lower complexity if doing so reduces task_score. Structure complexity is only penalised when it adds no performance gain.

# Proposal Context

## Task Specification

- Task name: grasp_place
- Frozen realised-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`
- Frozen object start: [0.5125095466604667, 0.039721380096957554, 0.03]
- Frozen task target: [0.6275685690245193, 0.17252071899905919, 0.14502494273668382]
- Goal object position: (0.6275685690245193, 0.17252071899905919, 0.14502494273668382)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6275685690245193, 0.17252071899905919, 0.14502494273668382)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5125095466604667, 0.039721380096957554, 0.03)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: franka_hand
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: grasp_target
    role: manipulated_object
    dynamics: free
    geometry: box
    dimensions_m: [0.04, 0.04, 0.06]
    mass_kg: 0.05
  - name: placement_surface
    role: goal_area
    dynamics: static
    geometry: point
task_landmarks:
  frozen_object_start: [0.5125, 0.0397, 0.03]
  frozen_task_target: [0.6276, 0.1725, 0.145]
  frozen_object_starts: {'grasp_target': [0.5125095466604667, 0.039721380096957554, 0.03]}
  frozen_targets: {'place_target': [0.6275685690245193, 0.17252071899905919, 0.14502494273668382]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6

## Subtask Layer

**Mode**: free (you define subtask targets; use `subtasks:` block in your YAML)

Define subtasks in a `subtasks:` block **before** `phases:`. Each subtask specifies an intermediate optimisation target.

**Required fields** — always include both, never omit:
- `anchor` (**required**): fixture | goal | object | world
- `target_entity` (**required**): hinge | object | tcp

Subtask anchors are separate from phase `target.anchor` vocabulary: subtasks use `world | object | goal | fixture`, while phase targets use `world | task_goal | task_object | fixture | body | site | current_tcp`.

Optional fields:
- `metric`: contact | distance | goal_progress | hinge_angle (default: distance)
- `offset`: [x, y, z] in metres relative to anchor (default: [0, 0, 0])
- `param_offset_key`: CMA-ES parameter added to offset at runtime (optional)
- `weight`: scoring weight [0.1, 1.0] (default: 1.0)

**Anchor resolution for this task** — choose anchor so the resolved position is meaningful:
| Anchor | Resolves to | Best used for |
|--------|-------------|---------------|
| `world` | absolute world-frame coordinate | fixed reference points not tied to objects |
| `object` | offset from object initial position (0.5125095466604667, 0.039721380096957554, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.6275685690245193, 0.17252071899905919, 0.14502494273668382) | final destination targets |
| `fixture` | offset from fixture pose (if defined, else world) | targets near fixture |

Annotate each phase with `subtask_id: <id>` to bind it to a subtask.
Only the **last phase** bound to a given subtask contributes to subtask scoring.

Example (two subtasks — one near object start, one at goal):
```yaml
subtasks:
  - id: reach_pre_contact
    anchor: object         # resolved to object initial position (see table above)
    target_entity: tcp     # score TCP distance to this target
    metric: distance
    offset: [0.0, 0.0, 0.10]  # 10 cm above object start position
    weight: 0.3
  - id: reach_goal
    anchor: goal           # resolved to task goal position (see table above)
    target_entity: tcp
    metric: distance
    offset: [0.0, 0.0, 0.0]
    weight: 0.7
phases:
  - id: approach_1
    type: approach
    subtask_id: reach_pre_contact
    ...
  - id: push_1
    type: push
    subtask_id: reach_goal
    ...
```

## Current Skill (Q=-0.050) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.3
- id: transport_goal
  weight: 0.7
phases:
- id: approach_object
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.02
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_object
- id: descend_to_grasp
  type: descend
  generator: linear_cartesian
  control: force_threshold_switch
  termination: contact_detected
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.035
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
- id: grasp_object
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  parameters:
    guard_threshold:
      type: scalar
      range:
      - 0.3
      - 0.8
      default: 0.5
      binds_to:
      - path: guards.check_grasp.threshold
        mode: replace
  guards:
  - id: check_grasp
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.005
- id: lift_object
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.08
      - 0.2
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: check_lift
    when: after_phase
    predicate: object_lifted
    threshold: 0.02
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.01
- id: transport_to_goal
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: transport_goal
- id: descend_to_place
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
- id: release_object
  type: release
  control: position_control
  termination: time_limit
  end_effector_action: open
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
- id: retract_after_place
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.02
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.035]
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **grasp_object** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - guard_threshold: status=consumed; consumers=guards.check_grasp.threshold (replace)
  - guards:
    - id=check_grasp, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.005]
- **lift_object** (`lift`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=check_lift, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.02
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.01]
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **release_object** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **retract_after_place** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.050
- **task_score** (E): 0.255
- **fitness_score**: 0.580  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.630

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1574 |
| descend_to_grasp | 1.00 | 1.00 | 0.0847 |
| grasp_object | 1.00 | 1.00 | 0.0116 |
| lift_object | 1.00 | 1.00 | 0.1024 |
| transport_to_goal | 1.00 | 1.00 | 0.2387 |
| descend_to_place | 1.00 | 1.00 | 0.0668 |
| release_object | 1.00 | 1.00 | 0.0197 |
| retract_after_place | 1.00 | 1.00 | 0.1199 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.019, 0.148) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 | 1.00 / 4.000 | 0.123 | 0.123 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.506, 0.019, 0.148)→(0.506, 0.022, 0.064) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 27.333 | 0.148 | 0.201 |
| grasp_object | grasp | 1.00 / step_budget | (0.506, 0.022, 0.064)→(0.498, 0.022, 0.055) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 16.667 | 0.128 | 0.304 |
| lift_object | lift | 1.00 / step_budget | (0.498, 0.022, 0.055)→(0.506, 0.022, 0.157) | (0.511, 0.022, 0.026)→(0.513, 0.022, 0.122) | 0.273→0.226 | 1.00 / 8.000 | 6499.292 | 1.629 |
| transport_to_goal | approach | 1.00 / step_budget | (0.506, 0.022, 0.157)→(0.599, 0.200, 0.279) | (0.513, 0.022, 0.122)→(0.563, 0.109, 0.016) | 0.226→0.221 | 1.00 / 8.333 | 91002.783 | 0.123 |
| descend_to_place | descend | 1.00 / step_budget | (0.599, 0.200, 0.279)→(0.602, 0.206, 0.213) | (0.563, 0.109, 0.016)→(0.563, 0.109, 0.016) | 0.221→0.221 | 1.00 / 4.000 | 0.123 | 0.123 |
| release_object | release | 1.00 / step_budget | (0.602, 0.206, 0.213)→(0.597, 0.204, 0.232) | (0.563, 0.109, 0.016)→(0.563, 0.109, 0.016) | 0.221→0.221 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract_after_place | retract | 1.00 / step_budget | (0.597, 0.204, 0.232)→(0.595, 0.203, 0.351) | (0.563, 0.109, 0.016)→(0.563, 0.109, 0.016) | 0.221→0.221 | 1.00 / 4.000 | 0.123 | 0.138 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.416
- phase_score: 0.325
- phase_breakdown.transport_goal_score: 0.177
- phase_breakdown.approach_object_score: 0.671
- grasp_place_fitness: 0.663

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.663
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.416
- **Median Q (composite search score)**: -0.069
- **K-run variance**: 0.0038
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.304


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `0b279c554151a1bc107b4895d67067efa2444eadb5a644f2482f57ab9ff93d7f`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `079d4532bc3cff86c1b89933c7940f2ee474dc4233e12f8d134c76ceb3cd8d4d`; realized-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51251,0.03972,0.03]},{"name":"goal","value":[0.62757,0.17252,0.14502]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.51251,0.03972,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.62757,0.17252,0.14502]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.64019,"average_solve_count":214.0,"average_success_count":214.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.speed":0.10784,"descend_to_grasp.speed":0.03482,"descend_to_place.speed":0.03138,"grasp_object.guard_threshold":0.68192,"lift_object.lift_height":0.13758,"lift_object.speed":0.14248,"retract_after_place.retract_height":0.16585,"retract_after_place.speed":0.15368,"transport_to_goal.speed":0.15506},"optimized_scores":{"best_composite_score":0.03286,"best_fitness_score":0.66286,"best_task_score":0.41565},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":563.0,"contact_point_centroid":[0.60285,0.16309,-0.00375],"force_p95":0.81877,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.55474,"mean_force":0.20251,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.60414,0.14871,0.21998]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2945.0,"contact_point_centroid":[0.50413,0.01983,0.09257],"force_p95":0.14221,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34067,"mean_force":0.10203,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.5018,0.0382,0.09552]},{"body_a":"world","body_b":"grasp_target","contact_count":83.0,"contact_point_centroid":[0.51108,0.03807,-0.00139],"force_p95":0.29066,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.31247,"mean_force":0.0576,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49896,0.03824,0.05412]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3157.0,"contact_point_centroid":[0.50367,0.05656,0.08999],"force_p95":0.14175,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30948,"mean_force":0.09645,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50157,0.0382,0.09281]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2640.0,"contact_point_centroid":[0.54577,0.05969,0.16518],"force_p95":0.15948,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25007,"mean_force":0.11663,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54035,0.07785,0.16888]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2976.0,"contact_point_centroid":[0.54678,0.0969,0.16568],"force_p95":0.13862,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21376,"mean_force":0.10396,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54134,0.07897,0.16966]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51254,0.03961,-0.00211],"force_p95":0.15487,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2085,"mean_force":0.13069,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50105,0.03843,0.05388]},{"body_a":"world","body_b":"grasp_target","contact_count":1180.0,"contact_point_centroid":[0.51251,0.03972,-0.00189],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12304,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50305,0.01634,0.22518]},{"body_a":"world","body_b":"grasp_target","contact_count":524.0,"contact_point_centroid":[0.60275,0.1634,-0.00199],"force_p95":0.12302,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12339,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61873,0.16578,0.19959]},{"body_a":"world","body_b":"grasp_target","contact_count":2288.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.506,0.03642,0.10099]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.60275,0.1634,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61647,0.16732,0.16221]},{"body_a":"world","body_b":"grasp_target","contact_count":2032.0,"contact_point_centroid":[0.60275,0.1634,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.61251,0.16599,0.25425]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2457.0,"contact_point_centroid":[0.50108,0.01961,0.05029],"force_p95":0.10511,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11794,"mean_force":0.08149,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49992,0.03834,0.05261]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3443.0,"contact_point_centroid":[0.50175,0.05704,0.05074],"force_p95":0.09793,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09951,"mean_force":0.06066,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49992,0.03834,0.05261]},{"body_a":"left_finger","body_b":"right_finger","contact_count":357.0,"contact_point_centroid":[0.60998,0.15489,0.22672],"force_p95":0.01435,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01627,"mean_force":0.01101,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.60974,0.15487,0.22446]},{"body_a":"left_finger","body_b":"right_finger","contact_count":558.0,"contact_point_centroid":[0.61896,0.16579,0.20221],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01274,"mean_force":0.01046,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61872,0.16577,0.19975]}],"total_contact_groups":17},"final_pose_error":0.01984,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.60275,0.1634,0.01602],"final_tcp_position":[0.61307,0.16612,0.32788],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":9748.92038,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":296.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2288.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_object","tcp_end":[0.50763,0.03385,0.14844],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12266,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":572.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15046,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7700.0,"raw_peak_contact_force":0.2085,"tcp_end":[0.50758,0.03896,0.06133],"tcp_start":[0.50763,0.03385,0.14844],"tcp_to_object_dist_end":0.03566,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51246,0.03872,0.02562],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.2131,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12808,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":6185.0,"raw_peak_contact_force":0.34067,"tcp_end":[0.49989,0.03834,0.05257],"tcp_start":[0.50758,0.03896,0.06133],"tcp_to_object_dist_end":0.02974,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":297.0,"n_steps_budget":600.0,"object_pos_end":[0.51651,0.03882,0.11192],"object_pos_start":[0.51246,0.03872,0.02562],"object_to_goal_dist_end":0.17694,"object_to_goal_dist_start":0.2131,"object_z_max":0.11166,"peak_contact_force":9748.92038,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":6536.0,"raw_peak_contact_force":1.55474,"tcp_end":[0.50723,0.03836,0.14404],"tcp_start":[0.49989,0.03834,0.05257],"tcp_to_object_dist_end":0.03344,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":567.0,"n_steps_budget":1000.0,"object_pos_end":[0.60277,0.16341,0.016],"object_pos_start":[0.51651,0.03882,0.11192],"object_to_goal_dist_end":0.1317,"object_to_goal_dist_start":0.17694,"object_z_max":0.15512,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1082.0,"raw_peak_contact_force":0.12339,"subtask_id":"transport_goal","tcp_end":[0.61737,0.16336,0.23057],"tcp_start":[0.50723,0.03836,0.14404],"tcp_to_object_dist_end":0.21507,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":131.0,"n_steps_budget":1000.0,"object_pos_end":[0.60275,0.1634,0.01602],"object_pos_start":[0.60277,0.16341,0.016],"object_to_goal_dist_end":0.13169,"object_to_goal_dist_start":0.1317,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62131,0.16873,0.16329],"tcp_start":[0.61737,0.16336,0.23057],"tcp_to_object_dist_end":0.14854,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60275,0.1634,0.01602],"object_pos_start":[0.60275,0.1634,0.01602],"object_to_goal_dist_end":0.13169,"object_to_goal_dist_start":0.13169,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2032.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61486,0.16679,0.18177],"tcp_start":[0.62131,0.16873,0.16329],"tcp_to_object_dist_end":0.16623,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":508.0,"n_steps_budget":690.0,"object_pos_end":[0.60275,0.1634,0.01602],"object_pos_start":[0.60275,0.1634,0.01602],"object_to_goal_dist_end":0.13169,"object_to_goal_dist_start":0.13169,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1180.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.61307,0.16612,0.32788],"tcp_start":[0.61486,0.16679,0.18177],"tcp_to_object_dist_end":0.31204,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `a74f7c08b88460953bfa7e35b953cddf9278fdc17d2d4db8a2ea121b328e8b73`; realized-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.4827,0.04873,0.03]},{"name":"goal","value":[0.58187,0.22885,0.23048]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.4827,0.04873,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58187,0.22885,0.23048]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.6,"average_solve_count":280.0,"average_success_count":280.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.speed":0.07677,"descend_to_grasp.speed":0.03364,"descend_to_place.speed":0.04159,"grasp_object.guard_threshold":0.39265,"lift_object.lift_height":0.15337,"lift_object.speed":0.08715,"retract_after_place.retract_height":0.15286,"retract_after_place.speed":0.11011,"transport_to_goal.speed":0.07142},"optimized_scores":{"best_composite_score":-0.06943,"best_fitness_score":0.56057,"best_task_score":0.21683},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1830.0,"contact_point_centroid":[0.53374,0.16347,-0.00256],"force_p95":0.25306,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.74336,"mean_force":0.15097,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54914,0.17526,0.27372]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3161.0,"contact_point_centroid":[0.47452,0.06526,0.09862],"force_p95":0.15538,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29448,"mean_force":0.10791,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47242,0.04697,0.10228]},{"body_a":"world","body_b":"grasp_target","contact_count":78.0,"contact_point_centroid":[0.48152,0.04694,-0.00146],"force_p95":0.25724,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.28717,"mean_force":0.05739,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47002,0.04691,0.05658]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3203.0,"contact_point_centroid":[0.4738,0.02872,0.09746],"force_p95":0.15262,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26751,"mean_force":0.10451,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47228,0.04697,0.10039]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2191.0,"contact_point_centroid":[0.49843,0.06066,0.18147],"force_p95":0.16209,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25393,"mean_force":0.12052,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49348,0.07884,0.18521]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48275,0.04868,-0.00212],"force_p95":0.15797,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21212,"mean_force":0.13142,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47202,0.04713,0.05636]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2648.0,"contact_point_centroid":[0.49928,0.09772,0.18189],"force_p95":0.12116,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2054,"mean_force":0.09931,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49409,0.07989,0.18618]},{"body_a":"world","body_b":"grasp_target","contact_count":1204.0,"contact_point_centroid":[0.4827,0.04873,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12303,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49051,0.02003,0.22535]},{"body_a":"world","body_b":"grasp_target","contact_count":2128.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47842,0.0446,0.10322]},{"body_a":"world","body_b":"grasp_target","contact_count":504.0,"contact_point_centroid":[0.53365,0.16362,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57598,0.22194,0.28415]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.53365,0.16362,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57439,0.22349,0.24897]},{"body_a":"world","body_b":"grasp_target","contact_count":1944.0,"contact_point_centroid":[0.53365,0.16362,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.57195,0.22218,0.33455]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2858.0,"contact_point_centroid":[0.47085,0.02833,0.05195],"force_p95":0.09287,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11315,"mean_force":0.07109,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47095,0.04703,0.05523]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2817.0,"contact_point_centroid":[0.47147,0.06584,0.05177],"force_p95":0.09978,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10021,"mean_force":0.07375,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47096,0.04703,0.05523]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1730.0,"contact_point_centroid":[0.55238,0.18032,0.28063],"force_p95":0.01181,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0162,"mean_force":0.01061,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55208,0.18029,0.27838]},{"body_a":"left_finger","body_b":"right_finger","contact_count":527.0,"contact_point_centroid":[0.57628,0.22198,0.28625],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01279,"mean_force":0.01063,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57598,0.22195,0.28405]}],"total_contact_groups":17},"final_pose_error":0.01983,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.53365,0.16362,0.01602],"final_tcp_position":[0.57247,0.22234,0.40185],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":273008.1045,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":302.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2128.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_object","tcp_end":[0.48182,0.04159,0.14845],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12264,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":532.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.15418,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7475.0,"raw_peak_contact_force":0.21212,"tcp_end":[0.47826,0.04774,0.06303],"tcp_start":[0.48182,0.04159,0.14845],"tcp_to_object_dist_end":0.03729,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48267,0.04776,0.02558],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.2909,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.14204,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":6442.0,"raw_peak_contact_force":0.29448,"tcp_end":[0.47092,0.04703,0.0552],"tcp_start":[0.47826,0.04774,0.06303],"tcp_to_object_dist_end":0.03187,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":337.0,"n_steps_budget":900.0,"object_pos_end":[0.48472,0.04729,0.1246],"object_pos_start":[0.48267,0.04776,0.02558],"object_to_goal_dist_end":0.23155,"object_to_goal_dist_start":0.2909,"object_z_max":0.12432,"peak_contact_force":9748.83231,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":8399.0,"raw_peak_contact_force":1.74336,"tcp_end":[0.47775,0.0473,0.1596],"tcp_start":[0.47092,0.04703,0.0552],"tcp_to_object_dist_end":0.03569,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":848.0,"n_steps_budget":1000.0,"object_pos_end":[0.53365,0.16362,0.01602],"object_pos_start":[0.48472,0.04729,0.1246],"object_to_goal_dist_end":0.22929,"object_to_goal_dist_start":0.23155,"object_z_max":0.17402,"peak_contact_force":273008.1045,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1031.0,"raw_peak_contact_force":0.12263,"subtask_id":"transport_goal","tcp_end":[0.57491,0.21941,0.31446],"tcp_start":[0.47775,0.0473,0.1596],"tcp_to_object_dist_end":0.3064,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":126.0,"n_steps_budget":1000.0,"object_pos_end":[0.53365,0.16362,0.01602],"object_pos_start":[0.53365,0.16362,0.01602],"object_to_goal_dist_end":0.22929,"object_to_goal_dist_start":0.22929,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1026.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57769,0.22493,0.24918],"tcp_start":[0.57491,0.21941,0.31446],"tcp_to_object_dist_end":0.24507,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53365,0.16362,0.01602],"object_pos_start":[0.53365,0.16362,0.01602],"object_to_goal_dist_end":0.22929,"object_to_goal_dist_start":0.22929,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1944.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57337,0.22295,0.26879],"tcp_start":[0.57769,0.22493,0.24918],"tcp_to_object_dist_end":0.26266,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":486.0,"n_steps_budget":870.0,"object_pos_end":[0.53365,0.16362,0.01602],"object_pos_start":[0.53365,0.16362,0.01602],"object_to_goal_dist_end":0.22929,"object_to_goal_dist_start":0.22929,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1204.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.57247,0.22234,0.40185],"tcp_start":[0.57337,0.22295,0.26879],"tcp_to_object_dist_end":0.3922,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `b1a72366a9c9a56aa2e80fc4399e157c8281abf492ab3c1ede02058762a86ed7`; realized-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53702,-0.02132,0.03]},{"name":"goal","value":[0.61031,0.22775,0.20741]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.53702,-0.02132,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61031,0.22775,0.20741]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.64228,"average_solve_count":246.0,"average_success_count":246.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.speed":0.09556,"descend_to_grasp.speed":0.04997,"descend_to_place.speed":0.04244,"grasp_object.guard_threshold":0.77239,"lift_object.lift_height":0.16122,"lift_object.speed":0.08363,"retract_after_place.retract_height":0.10017,"retract_after_place.speed":0.08261,"transport_to_goal.speed":0.08196},"optimized_scores":{"best_composite_score":-0.11447,"best_fitness_score":0.51553,"best_task_score":0.13341},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2908.0,"contact_point_centroid":[0.55362,0.00097,-0.0023],"force_p95":0.1286,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.58889,"mean_force":0.1372,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5747,0.12328,0.24164]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3506.0,"contact_point_centroid":[0.5284,-0.0023,0.10362],"force_p95":0.14681,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2762,"mean_force":0.10837,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52548,-0.02064,0.10798]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3826.0,"contact_point_centroid":[0.52823,-0.03883,0.10296],"force_p95":0.13907,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27129,"mean_force":0.10087,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.5254,-0.02064,0.10727]},{"body_a":"world","body_b":"grasp_target","contact_count":85.0,"contact_point_centroid":[0.53557,-0.02048,-0.00136],"force_p95":0.24242,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26882,"mean_force":0.05725,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52235,-0.02061,0.05868]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":668.0,"contact_point_centroid":[0.53999,0.0091,0.16647],"force_p95":0.1712,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2462,"mean_force":0.11878,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53391,-0.00909,0.17162]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53705,-0.02128,-0.00206],"force_p95":0.14029,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18155,"mean_force":0.12704,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52454,-0.02066,0.05876]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":839.0,"contact_point_centroid":[0.53988,-0.02517,0.16747],"force_p95":0.12715,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16959,"mean_force":0.09263,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53431,-0.00734,0.17231]},{"body_a":"world","body_b":"grasp_target","contact_count":1208.0,"contact_point_centroid":[0.53702,-0.02132,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12303,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51329,-0.00883,0.22471]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52911,-0.01992,0.0929]},{"body_a":"world","body_b":"grasp_target","contact_count":504.0,"contact_point_centroid":[0.55361,0.00093,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60506,0.21915,0.2615]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.55361,0.00093,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.60252,0.22155,0.22479]},{"body_a":"world","body_b":"grasp_target","contact_count":1296.0,"contact_point_centroid":[0.55361,0.00093,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.5995,0.22013,0.28387]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2667.0,"contact_point_centroid":[0.52375,-0.00189,0.05343],"force_p95":0.09715,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10484,"mean_force":0.07633,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52337,-0.02064,0.05736]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2956.0,"contact_point_centroid":[0.52392,-0.03932,0.05344],"force_p95":0.09223,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09234,"mean_force":0.06969,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52337,-0.02064,0.05736]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2813.0,"contact_point_centroid":[0.57774,0.13209,0.2488],"force_p95":0.01106,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01627,"mean_force":0.01058,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.57755,0.13209,0.24651]},{"body_a":"left_finger","body_b":"right_finger","contact_count":542.0,"contact_point_centroid":[0.60519,0.21916,0.26377],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01271,"mean_force":0.01037,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60505,0.21915,0.26152]}],"total_contact_groups":17},"final_pose_error":0.01977,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.55361,0.00093,0.01602],"final_tcp_position":[0.59958,0.22011,0.32477],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":1.58889,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":303.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_object","tcp_end":[0.52874,-0.01827,0.14773],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12203,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13926,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7423.0,"raw_peak_contact_force":0.18155,"tcp_end":[0.53118,-0.0208,0.0668],"tcp_start":[0.52874,-0.01827,0.14773],"tcp_to_object_dist_end":0.0412,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53697,-0.02085,0.02579],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.3165,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.11475,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7417.0,"raw_peak_contact_force":0.2762,"tcp_end":[0.52334,-0.02064,0.05732],"tcp_start":[0.53118,-0.0208,0.0668],"tcp_to_object_dist_end":0.03435,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":387.0,"n_steps_budget":990.0,"object_pos_end":[0.53825,-0.02115,0.13028],"object_pos_start":[0.53697,-0.02085,0.02579],"object_to_goal_dist_end":0.27036,"object_to_goal_dist_start":0.3165,"object_z_max":0.13002,"peak_contact_force":0.12263,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":7228.0,"raw_peak_contact_force":1.58889,"tcp_end":[0.53179,-0.02073,0.16776],"tcp_start":[0.52334,-0.02064,0.05732],"tcp_to_object_dist_end":0.03803,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":894.0,"n_steps_budget":1000.0,"object_pos_end":[0.55361,0.00093,0.01602],"object_pos_start":[0.53825,-0.02115,0.13028],"object_to_goal_dist_end":0.30215,"object_to_goal_dist_start":0.27036,"object_z_max":0.13694,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1046.0,"raw_peak_contact_force":0.12263,"subtask_id":"transport_goal","tcp_end":[0.60458,0.21579,0.29255],"tcp_start":[0.53179,-0.02073,0.16776],"tcp_to_object_dist_end":0.35388,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":126.0,"n_steps_budget":1000.0,"object_pos_end":[0.55361,0.00093,0.01602],"object_pos_start":[0.55361,0.00093,0.01602],"object_to_goal_dist_end":0.30215,"object_to_goal_dist_start":0.30215,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1018.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.60623,0.22302,0.22585],"tcp_start":[0.60458,0.21579,0.29255],"tcp_to_object_dist_end":0.31003,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55361,0.00093,0.01602],"object_pos_start":[0.55361,0.00093,0.01602],"object_to_goal_dist_end":0.30215,"object_to_goal_dist_start":0.30215,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1296.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.60134,0.22098,0.24427],"tcp_start":[0.60623,0.22302,0.22585],"tcp_to_object_dist_end":0.32062,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":324.0,"n_steps_budget":780.0,"object_pos_end":[0.55361,0.00093,0.01602],"object_pos_start":[0.55361,0.00093,0.01602],"object_to_goal_dist_end":0.30215,"object_to_goal_dist_start":0.30215,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1208.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.59958,0.22011,0.32477],"tcp_start":[0.60134,0.22098,0.24427],"tcp_to_object_dist_end":0.38141,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```