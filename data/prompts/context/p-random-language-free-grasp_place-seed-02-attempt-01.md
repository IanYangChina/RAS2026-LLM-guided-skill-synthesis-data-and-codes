## Search State

- **Seed**: 2
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | impedance_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | contact_detected | time_limit | pose_tolerance | 15 | -0.2570 | 0.39 | ✅ accepted |
| 0 | align → align → pull → descend | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | admittance_control | pose_tolerance | pose_tolerance | pose_tolerance | contact_detected | 0 | 0.1073 | 0.16 | ✅ accepted |

**Proposal policy**: task_score is 0.39 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`
- Frozen object start: [0.4761612134249316, -0.02015088565858767, 0.03]
- Frozen task target: [0.631422574059428, 0.1591915942135097, 0.1900150788948481]
- Goal object position: (0.631422574059428, 0.1591915942135097, 0.1900150788948481)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.631422574059428, 0.1591915942135097, 0.1900150788948481)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.4761612134249316, -0.02015088565858767, 0.03)
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
  frozen_object_start: [0.4762, -0.0202, 0.03]
  frozen_task_target: [0.6314, 0.1592, 0.19]
  frozen_object_starts: {'grasp_target': [0.4761612134249316, -0.02015088565858767, 0.03]}
  frozen_targets: {'place_target': [0.631422574059428, 0.1591915942135097, 0.1900150788948481]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a

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
| `object` | offset from object initial position (0.4761612134249316, -0.02015088565858767, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.631422574059428, 0.1591915942135097, 0.1900150788948481) | final destination targets |
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

## Current Skill (Q=-0.257) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
subtasks:
- id: reach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.12
  weight: 0.3
- id: reach_goal
  offset:
  - 0.0
  - 0.0
  - 0.12
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
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.12
    tolerance: 0.03
    orientation:
      mode: keep_current
  parameters:
    approach_offset_z:
      type: scalar
      range:
      - 0.08
      - 0.15
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
    tolerance:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: reach_object
- id: descend_grasp
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: contact_detected
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.02
    orientation:
      mode: keep_current
  parameters:
    descend_offset_z:
      type: scalar
      range:
      - 0.0
      - 0.04
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
- id: grasp
  type: grasp
  control: impedance_control
  termination: grasp_success
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: none
- id: lift
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.03
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.12
      binds_to:
      - path: generator.speed
        mode: replace
    tolerance:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
- id: transport_approach
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.12
    tolerance: 0.03
    orientation:
      mode: keep_current
  parameters:
    place_approach_z:
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
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
    tolerance:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: reach_goal
- id: descend_place
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: contact_detected
  target:
    source: yaml
    anchor: task_goal
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    place_descend_z:
      type: scalar
      range:
      - 0.0
      - 0.04
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
- id: release_retract
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
    orientation:
      mode: none
- id: retract
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
    - 0.15
    tolerance: 0.05
    orientation:
      mode: keep_current
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.12], tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_offset_z: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
    - tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **descend_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.02]
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_offset_z: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=none
  - parameter_bindings: none
- **lift** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15], tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
    - tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **transport_approach** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=grasp_target, offset=[0.0, 0.0, 0.12], tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_approach_z: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
    - tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **descend_place** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=grasp_target, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_descend_z: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **release_retract** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=none
  - parameter_bindings: none
- **retract** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15], tolerance=0.05
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.257
- **task_score** (E): 0.388
- **fitness_score**: 0.673  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.930

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1397 |
| descend_grasp | 1.00 | 1.00 | 0.1269 |
| grasp | 1.00 | 1.00 | 0.0113 |
| lift | 1.00 | 1.00 | 0.1008 |
| transport_approach | 1.00 | 1.00 | 0.2508 |
| descend_place | 1.00 | 1.00 | 0.0558 |
| release_retract | 1.00 | 1.00 | 0.0200 |
| retract | 1.00 | 1.00 | 0.1861 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.492, -0.012, 0.165) | (0.493, -0.015, 0.030)→(0.493, -0.015, 0.026) | 0.279→0.281 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_grasp | descend | 1.00 / step_budget | (0.492, -0.012, 0.165)→(0.488, -0.015, 0.039) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.488, -0.015, 0.039)→(0.481, -0.015, 0.031) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 45.000 | 0.134 | 0.175 |
| lift | lift | 1.00 / step_budget | (0.481, -0.015, 0.031)→(0.477, -0.015, 0.131) | (0.493, -0.015, 0.026)→(0.496, -0.015, 0.124) | 0.281→0.243 | 1.00 / 27.000 | 19.669 | 0.668 |
| transport_approach | approach | 1.00 / step_budget | (0.477, -0.015, 0.131)→(0.621, 0.158, 0.237) | (0.496, -0.015, 0.124)→(0.633, 0.155, 0.140) | 0.243→0.095 | 1.00 / 16.000 | 0.085 | 0.924 |
| descend_place | descend | 1.00 / step_budget | (0.621, 0.158, 0.237)→(0.632, 0.173, 0.185) | (0.633, 0.155, 0.140)→(0.636, 0.168, 0.042) | 0.095→0.124 | 1.00 / 14.333 | 0.115 | 0.872 |
| release_retract | release | 1.00 / step_budget | (0.632, 0.173, 0.185)→(0.627, 0.172, 0.204) | (0.636, 0.168, 0.042)→(0.629, 0.167, 0.019) | 0.124→0.147 | 1.00 / 4.000 | 0.144 | 0.449 |
| retract | retract | 1.00 / step_budget | (0.627, 0.172, 0.204)→(0.629, 0.172, 0.390) | (0.629, 0.167, 0.019)→(0.628, 0.168, 0.019) | 0.147→0.147 | 1.00 / 4.000 | 0.123 | 0.145 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.544
- phase_score: 0.492
- phase_breakdown.reach_goal_score: 0.447
- phase_breakdown.reach_object_score: 0.598
- grasp_place_fitness: 0.753

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.753
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.544
- **Median Q (composite search score)**: -0.296
- **K-run variance**: 0.0032
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.305


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `dde525b5f1d1bd9dc458c18c8bb170b8849a392c0909c5e3e8e19baca2e18946`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `3eaf951d4314ad541ffae42f4c615c856bb77d128e3ae1cab520a1988305ba67`; realized-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47616,-0.02015,0.03]},{"name":"goal","value":[0.63142,0.15919,0.19002]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.47616,-0.02015,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63142,0.15919,0.19002]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.97076,"average_solve_count":171.0,"average_success_count":171.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_offset_z":0.09709,"approach_object.speed":0.28204,"approach_object.tolerance":0.02697,"descend_grasp.descend_offset_z":0.01038,"descend_grasp.speed":0.05851,"descend_place.place_descend_z":0.03865,"descend_place.speed":0.12359,"lift.lift_height":0.12092,"lift.speed":0.0808,"lift.tolerance":0.0149,"retract.retract_height":0.2223,"retract.speed":0.16066,"transport_approach.place_approach_z":0.08836,"transport_approach.speed":0.21389,"transport_approach.tolerance":0.02209},"optimized_scores":{"best_composite_score":-0.29603,"best_fitness_score":0.63397,"best_task_score":0.30952},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":208.0,"contact_point_centroid":[0.62953,0.13327,-0.00741],"force_p95":1.20695,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.21761,"mean_force":0.39285,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.60745,0.13529,0.2503]},{"body_a":"world","body_b":"grasp_target","contact_count":63.0,"contact_point_centroid":[0.47382,-0.01955,-0.00147],"force_p95":0.57573,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58582,"mean_force":0.21266,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46299,-0.0196,0.03213]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3874.0,"contact_point_centroid":[0.5189,0.05541,0.16871],"force_p95":0.12569,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31993,"mean_force":0.08491,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.51339,0.03703,0.16753]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3329.0,"contact_point_centroid":[0.46179,-0.00037,0.07523],"force_p95":0.09291,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28974,"mean_force":0.06072,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46112,-0.01954,0.0727]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3652.0,"contact_point_centroid":[0.46181,-0.03865,0.07498],"force_p95":0.08685,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28817,"mean_force":0.05632,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4611,-0.01954,0.07312]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3216.0,"contact_point_centroid":[0.51276,0.01216,0.16424],"force_p95":0.15626,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22382,"mean_force":0.09618,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.50756,0.03083,0.16243]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.02004,-0.00204],"force_p95":0.13603,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17664,"mean_force":0.12636,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46524,-0.01965,0.03215]},{"body_a":"world","body_b":"grasp_target","contact_count":752.0,"contact_point_centroid":[0.47616,-0.02015,-0.00183],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12328,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48964,-0.00767,0.23019]},{"body_a":"world","body_b":"grasp_target","contact_count":3292.0,"contact_point_centroid":[0.62868,0.13346,-0.00198],"force_p95":0.12335,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12908,"mean_force":0.12159,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.6221,0.15223,0.23257]},{"body_a":"world","body_b":"grasp_target","contact_count":2792.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.47349,-0.01795,0.0938]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.62868,0.13346,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_retract","phase_type":"release","tcp_position_centroid":[0.62403,0.1566,0.22098]},{"body_a":"world","body_b":"grasp_target","contact_count":804.0,"contact_point_centroid":[0.62868,0.13346,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.62303,0.15604,0.3215]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5069.0,"contact_point_centroid":[0.4638,-0.00041,0.0336],"force_p95":0.06577,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09547,"mean_force":0.04286,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46412,-0.01963,0.03104]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5153.0,"contact_point_centroid":[0.46404,-0.03888,0.03301],"force_p95":0.06644,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08698,"mean_force":0.04303,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46412,-0.01963,0.03104]},{"body_a":"left_finger","body_b":"right_finger","contact_count":40.0,"contact_point_centroid":[0.61502,0.14278,0.25914],"force_p95":0.0161,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0161,"mean_force":0.01367,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.61469,0.14278,0.25663]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3554.0,"contact_point_centroid":[0.62261,0.15226,0.23484],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01531,"mean_force":0.01037,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62212,0.15225,0.23252]}],"total_contact_groups":17},"final_pose_error":0.04987,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.62868,0.13346,0.01602],"final_tcp_position":[0.62512,0.15654,0.41275],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":58.7931,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":189.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":752.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.47869,-0.01606,0.15613],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1302,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":698.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2792.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.47175,-0.0198,0.03863],"tcp_start":[0.47869,-0.01606,0.15613],"tcp_to_object_dist_end":0.01336,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47604,-0.01969,0.02583],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28827,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13423,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12022.0,"raw_peak_contact_force":0.17664,"tcp_end":[0.46409,-0.01963,0.03101],"tcp_start":[0.47175,-0.0198,0.03863],"tcp_to_object_dist_end":0.01303,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":180.0,"n_steps_budget":930.0,"object_pos_end":[0.47759,-0.01941,0.11605],"object_pos_start":[0.47604,-0.01969,0.02583],"object_to_goal_dist_end":0.24705,"object_to_goal_dist_start":0.28827,"object_z_max":0.11556,"peak_contact_force":58.7931,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":7044.0,"raw_peak_contact_force":0.58582,"tcp_end":[0.4608,-0.01951,0.12225],"tcp_start":[0.46409,-0.01963,0.03101],"tcp_to_object_dist_end":0.0179,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":7.0,"n_steps":464.0,"n_steps_budget":1000.0,"object_pos_end":[0.62854,0.13495,0.01417],"object_pos_start":[0.47759,-0.01941,0.11605],"object_to_goal_dist_end":0.17753,"object_to_goal_dist_start":0.24705,"object_z_max":0.19276,"peak_contact_force":0.0,"phase_name":"transport_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7338.0,"raw_peak_contact_force":2.21761,"subtask_id":"reach_goal","tcp_end":[0.61608,0.14432,0.25789],"tcp_start":[0.4608,-0.01951,0.12225],"tcp_to_object_dist_end":0.24421,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":823.0,"n_steps_budget":1000.0,"object_pos_end":[0.62868,0.13346,0.01602],"object_pos_start":[0.62854,0.13495,0.01417],"object_to_goal_dist_end":0.17591,"object_to_goal_dist_start":0.17753,"object_z_max":0.01673,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6846.0,"raw_peak_contact_force":0.12908,"tcp_end":[0.6275,0.15764,0.22084],"tcp_start":[0.61608,0.14432,0.25789],"tcp_to_object_dist_end":0.20624,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62868,0.13346,0.01602],"object_pos_start":[0.62868,0.13346,0.01602],"object_to_goal_dist_end":0.17591,"object_to_goal_dist_start":0.17591,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_retract","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62275,0.15618,0.24026],"tcp_start":[0.6275,0.15764,0.22084],"tcp_to_object_dist_end":0.22547,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":201.0,"n_steps_budget":870.0,"object_pos_end":[0.62868,0.13346,0.01602],"object_pos_start":[0.62868,0.13346,0.01602],"object_to_goal_dist_end":0.17591,"object_to_goal_dist_start":0.17591,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":804.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62512,0.15654,0.41275],"tcp_start":[0.62275,0.15618,0.24026],"tcp_to_object_dist_end":0.39742,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `92fc0f2bbc35407e7976a239cbab7bb266e8a517486aa3be6bd6666f4c63f38d`; realized-scene SHA-256: `5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45856,-0.02632,0.03]},{"name":"goal","value":[0.63013,0.20822,0.11412]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.45856,-0.02632,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63013,0.20822,0.11412]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.32168,"average_solve_count":143.0,"average_success_count":143.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_offset_z":0.11549,"approach_object.speed":0.15307,"approach_object.tolerance":0.03212,"descend_grasp.descend_offset_z":0.00782,"descend_grasp.speed":0.12711,"descend_place.place_descend_z":0.0143,"descend_place.speed":0.17,"lift.lift_height":0.1256,"lift.speed":0.23483,"lift.tolerance":0.03245,"retract.retract_height":0.22303,"retract.speed":0.15997,"transport_approach.place_approach_z":0.10414,"transport_approach.speed":0.24695,"transport_approach.tolerance":0.03949},"optimized_scores":{"best_composite_score":-0.17701,"best_fitness_score":0.75299,"best_task_score":0.54447},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":215.0,"contact_point_centroid":[0.61714,0.20325,-0.0052],"force_p95":0.86919,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.1029,"mean_force":0.31381,"phase_index":6.0,"phase_name":"release_retract","phase_type":"release","tcp_position_centroid":[0.61848,0.20368,0.12897]},{"body_a":"world","body_b":"grasp_target","contact_count":59.0,"contact_point_centroid":[0.45606,-0.02564,-0.00146],"force_p95":0.67612,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.69803,"mean_force":0.24059,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44578,-0.02555,0.03067]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":893.0,"contact_point_centroid":[0.62729,0.22421,0.11678],"force_p95":0.09671,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3511,"mean_force":0.06408,"phase_index":6.0,"phase_name":"release_retract","phase_type":"release","tcp_position_centroid":[0.62297,0.20535,0.11716]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13395.0,"contact_point_centroid":[0.62259,0.17968,0.15321],"force_p95":0.11009,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30733,"mean_force":0.07184,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.61887,0.19857,0.15215]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3425.0,"contact_point_centroid":[0.44543,-0.0446,0.07364],"force_p95":0.09907,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30485,"mean_force":0.05902,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44437,-0.02548,0.07174]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3183.0,"contact_point_centroid":[0.44534,-0.00633,0.07435],"force_p95":0.10337,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30402,"mean_force":0.06247,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44438,-0.02548,0.07175]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14591.0,"contact_point_centroid":[0.62259,0.21708,0.15361],"force_p95":0.0957,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29035,"mean_force":0.0644,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.61876,0.19841,0.15289]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5895.0,"contact_point_centroid":[0.53478,0.06646,0.16543],"force_p95":0.13212,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2794,"mean_force":0.08351,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.53077,0.08516,0.16429]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5958.0,"contact_point_centroid":[0.53565,0.10419,0.16546],"force_p95":0.12129,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22861,"mean_force":0.08258,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.53113,0.08564,0.16444]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":912.0,"contact_point_centroid":[0.62694,0.1866,0.11707],"force_p95":0.09841,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20522,"mean_force":0.06011,"phase_index":6.0,"phase_name":"release_retract","phase_type":"release","tcp_position_centroid":[0.62307,0.20538,0.11734]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45857,-0.02618,-0.00206],"force_p95":0.14092,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19339,"mean_force":0.12758,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44812,-0.02563,0.03051]},{"body_a":"world","body_b":"grasp_target","contact_count":824.0,"contact_point_centroid":[0.60675,0.20586,-0.00198],"force_p95":0.16989,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19076,"mean_force":0.12322,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.61708,0.20296,0.22248]},{"body_a":"world","body_b":"grasp_target","contact_count":700.0,"contact_point_centroid":[0.45856,-0.02632,-0.00182],"force_p95":0.13762,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12333,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48346,-0.00977,0.23914]},{"body_a":"world","body_b":"grasp_target","contact_count":2732.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.45842,-0.02322,0.10189]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5296.0,"contact_point_centroid":[0.44647,-0.00635,0.03124],"force_p95":0.06519,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09972,"mean_force":0.04112,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44703,-0.02559,0.02948]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5418.0,"contact_point_centroid":[0.44647,-0.04488,0.03109],"force_p95":0.06544,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08065,"mean_force":0.04119,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44703,-0.02559,0.02948]}],"total_contact_groups":16},"final_pose_error":0.04966,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.6067,0.20587,0.02602],"final_tcp_position":[0.61844,0.20332,0.31376],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1.1029,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":176.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":700.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.46565,-0.02054,0.17399],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14826,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":683.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2732.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45445,-0.02586,0.03654],"tcp_start":[0.46565,-0.02054,0.17399],"tcp_to_object_dist_end":0.01131,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":48.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45845,-0.02568,0.02578],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30329,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.1387,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12514.0,"raw_peak_contact_force":0.19339,"tcp_end":[0.447,-0.02559,0.02945],"tcp_start":[0.45445,-0.02586,0.03654],"tcp_to_object_dist_end":0.01202,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":178.0,"n_steps_budget":600.0,"object_pos_end":[0.46227,-0.0254,0.11868],"object_pos_start":[0.45845,-0.02568,0.02578],"object_to_goal_dist_end":0.28771,"object_to_goal_dist_start":0.30329,"object_z_max":0.11819,"peak_contact_force":0.10648,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":6667.0,"raw_peak_contact_force":0.69803,"tcp_end":[0.44433,-0.02544,0.12541],"tcp_start":[0.447,-0.02559,0.02945],"tcp_to_object_dist_end":0.01916,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":475.0,"n_steps_budget":1000.0,"object_pos_end":[0.62445,0.18925,0.18151],"object_pos_start":[0.46227,-0.0254,0.11868],"object_to_goal_dist_end":0.07024,"object_to_goal_dist_start":0.28771,"object_z_max":0.1814,"peak_contact_force":0.10579,"phase_name":"transport_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":11853.0,"raw_peak_contact_force":0.2794,"subtask_id":"reach_goal","tcp_end":[0.61339,0.18911,0.20282],"tcp_start":[0.44433,-0.02544,0.12541],"tcp_to_object_dist_end":0.02401,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":956.0,"n_steps_budget":1000.0,"object_pos_end":[0.63065,0.20607,0.0938],"object_pos_start":[0.62445,0.18925,0.18151],"object_to_goal_dist_end":0.02044,"object_to_goal_dist_start":0.07024,"object_z_max":0.18156,"peak_contact_force":0.09865,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":27986.0,"raw_peak_contact_force":0.30733,"tcp_end":[0.62507,0.20606,0.1213],"tcp_start":[0.61339,0.18911,0.20282],"tcp_to_object_dist_end":0.02807,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60856,0.20488,0.02625],"object_pos_start":[0.63065,0.20607,0.0938],"object_to_goal_dist_end":0.09054,"object_to_goal_dist_start":0.02044,"object_z_max":0.0938,"peak_contact_force":0.18823,"phase_name":"release_retract","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2020.0,"raw_peak_contact_force":1.1029,"tcp_end":[0.61837,0.20364,0.14039],"tcp_start":[0.62507,0.20606,0.1213],"tcp_to_object_dist_end":0.11457,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":206.0,"n_steps_budget":870.0,"object_pos_end":[0.6067,0.20587,0.02602],"object_pos_start":[0.60856,0.20488,0.02625],"object_to_goal_dist_end":0.09119,"object_to_goal_dist_start":0.09054,"object_z_max":0.02625,"peak_contact_force":0.12318,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":824.0,"raw_peak_contact_force":0.19076,"tcp_end":[0.61844,0.20332,0.31376],"tcp_start":[0.61837,0.20364,0.14039],"tcp_to_object_dist_end":0.288,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `a3b2449a94ded39f3d450008c4da002b4ddf87103ab7d1b86900d116c316ff53`; realized-scene SHA-256: `1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54431,0.00113,0.03]},{"name":"goal","value":[0.64762,0.15808,0.1911]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.54431,0.00113,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.64762,0.15808,0.1911]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.16774,"average_solve_count":155.0,"average_success_count":155.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_offset_z":0.10876,"approach_object.speed":0.23828,"approach_object.tolerance":0.04057,"descend_grasp.descend_offset_z":0.01749,"descend_grasp.speed":0.19628,"descend_place.place_descend_z":0.02908,"descend_place.speed":0.17749,"lift.lift_height":0.14495,"lift.speed":0.18869,"lift.tolerance":0.03049,"retract.retract_height":0.26195,"retract.speed":0.11485,"transport_approach.place_approach_z":0.08024,"transport_approach.speed":0.1761,"transport_approach.tolerance":0.02279},"optimized_scores":{"best_composite_score":-0.29783,"best_fitness_score":0.63217,"best_task_score":0.31104},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2683.0,"contact_point_centroid":[0.64898,0.16358,-0.00247],"force_p95":0.1257,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.18019,"mean_force":0.14122,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.63979,0.15175,0.22097]},{"body_a":"world","body_b":"grasp_target","contact_count":64.0,"contact_point_centroid":[0.54092,0.00076,-0.00143],"force_p95":0.65787,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72033,"mean_force":0.21745,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52891,0.00085,0.03224]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3301.0,"contact_point_centroid":[0.52967,-0.01818,0.08309],"force_p95":0.11332,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.38705,"mean_force":0.07396,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52713,0.00081,0.08062]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3557.0,"contact_point_centroid":[0.52962,0.01972,0.08045],"force_p95":0.1129,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36933,"mean_force":0.06991,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52714,0.00081,0.07842]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":524.0,"contact_point_centroid":[0.63995,0.16118,0.24053],"force_p95":0.19599,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32031,"mean_force":0.11502,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.63418,0.14377,0.24402]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3426.0,"contact_point_centroid":[0.58407,0.05099,0.19791],"force_p95":0.15417,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27551,"mean_force":0.1092,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.57855,0.06969,0.19565]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":339.0,"contact_point_centroid":[0.64054,0.1254,0.24335],"force_p95":0.23766,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27349,"mean_force":0.14165,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.63408,0.14341,0.24601]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4606.0,"contact_point_centroid":[0.5855,0.08898,0.19714],"force_p95":0.13078,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20359,"mean_force":0.0868,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.5793,0.07073,0.19636]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5443,0.00101,-0.00203],"force_p95":0.13201,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15523,"mean_force":0.12538,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53173,0.0009,0.03263]},{"body_a":"world","body_b":"grasp_target","contact_count":740.0,"contact_point_centroid":[0.54431,0.00113,-0.00183],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12329,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51569,0.00042,0.23482]},{"body_a":"world","body_b":"grasp_target","contact_count":3688.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.53475,0.00094,0.09284]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.64897,0.16356,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_retract","phase_type":"release","tcp_position_centroid":[0.64007,0.15542,0.21167]},{"body_a":"world","body_b":"grasp_target","contact_count":1016.0,"contact_point_centroid":[0.64897,0.16356,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.6391,0.15489,0.33038]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4115.0,"contact_point_centroid":[0.53127,-0.01832,0.0339],"force_p95":0.07616,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11663,"mean_force":0.05177,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53047,0.00088,0.03118]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4878.0,"contact_point_centroid":[0.53124,0.01996,0.03302],"force_p95":0.06817,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.095,"mean_force":0.04474,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53047,0.00088,0.03118]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2662.0,"contact_point_centroid":[0.64054,0.15212,0.22249],"force_p95":0.01114,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0155,"mean_force":0.01053,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.64009,0.15211,0.22028]}],"total_contact_groups":17},"final_pose_error":0.04962,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.64897,0.16356,0.01602],"final_tcp_position":[0.64283,0.15587,0.44325],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":2.18019,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":186.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":740.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.53287,0.00086,0.16586],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1403,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":922.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3688.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53884,0.00103,0.04096],"tcp_start":[0.53287,0.00086,0.16586],"tcp_to_object_dist_end":0.01592,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54418,0.00075,0.02587],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25051,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13009,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.15523,"tcp_end":[0.53044,0.00088,0.03115],"tcp_start":[0.53884,0.00103,0.04096],"tcp_to_object_dist_end":0.01471,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":221.0,"n_steps_budget":600.0,"object_pos_end":[0.54711,0.00089,0.13665],"object_pos_start":[0.54418,0.00075,0.02587],"object_to_goal_dist_end":0.19437,"object_to_goal_dist_start":0.25051,"object_z_max":0.13618,"peak_contact_force":0.10866,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":6922.0,"raw_peak_contact_force":0.72033,"tcp_end":[0.52728,0.00082,0.14633],"tcp_start":[0.53044,0.00088,0.03115],"tcp_to_object_dist_end":0.02207,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":377.0,"n_steps_budget":1000.0,"object_pos_end":[0.64472,0.14188,0.22446],"object_pos_start":[0.54711,0.00089,0.13665],"object_to_goal_dist_end":0.0372,"object_to_goal_dist_start":0.19437,"object_z_max":0.22426,"peak_contact_force":0.15056,"phase_name":"transport_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8032.0,"raw_peak_contact_force":0.27551,"subtask_id":"reach_goal","tcp_end":[0.63386,0.14172,0.25046],"tcp_start":[0.52728,0.00082,0.14633],"tcp_to_object_dist_end":0.02818,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":822.0,"n_steps_budget":1000.0,"object_pos_end":[0.64897,0.16356,0.01602],"object_pos_start":[0.64472,0.14188,0.22446],"object_to_goal_dist_end":0.17518,"object_to_goal_dist_start":0.0372,"object_z_max":0.22461,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6208.0,"raw_peak_contact_force":2.18019,"tcp_end":[0.64366,0.15647,0.21198],"tcp_start":[0.63386,0.14172,0.25046],"tcp_to_object_dist_end":0.19616,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.64897,0.16356,0.01602],"object_pos_start":[0.64897,0.16356,0.01602],"object_to_goal_dist_end":0.17518,"object_to_goal_dist_start":0.17518,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_retract","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.63873,0.15499,0.23074],"tcp_start":[0.64366,0.15647,0.21198],"tcp_to_object_dist_end":0.21514,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":254.0,"n_steps_budget":1000.0,"object_pos_end":[0.64897,0.16356,0.01602],"object_pos_start":[0.64897,0.16356,0.01602],"object_to_goal_dist_end":0.17518,"object_to_goal_dist_start":0.17518,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1016.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.64283,0.15587,0.44325],"tcp_start":[0.63873,0.15499,0.23074],"tcp_to_object_dist_end":0.42734,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```