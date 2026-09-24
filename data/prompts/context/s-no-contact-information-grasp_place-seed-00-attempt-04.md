## Search State

- **Seed**: 0
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 10 | -0.0365 | 0.33 | ✅ accepted |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 10 | -0.0443 | 0.32 | ✅ accepted |
| 2 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | -0.0357 | 0.27 | ✅ accepted |
| 1 | approach → grasp → lift → approach → descend → release → retract | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | position_control | impedance_control | position_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | -0.1914 | 0.17 | ❌ rejected |
| 0 | insert → approach → push → retract → lift → insert → push | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | force_threshold_switch | position_control | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 8 | -0.1716 | 0.18 | ✅ accepted |

**Proposal policy**: task_score is 0.33 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `f07a678caf5b8ea43212ad5a337315ad102b1ae725b01cf669f7af9bd0eea2ea`
- Frozen object start: [0.5136961687321454, -0.02302132862361297, 0.03]
- Frozen task target: [0.5540973523936195, 0.15165276355285293, 0.22199053588004086]
- Goal object position: (0.5540973523936195, 0.15165276355285293, 0.22199053588004086)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5540973523936195, 0.15165276355285293, 0.22199053588004086)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5136961687321454, -0.02302132862361297, 0.03)
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
  frozen_object_start: [0.5137, -0.023, 0.03]
  frozen_task_target: [0.5541, 0.1517, 0.222]
  frozen_object_starts: {'grasp_target': [0.5136961687321454, -0.02302132862361297, 0.03]}
  frozen_targets: {'place_target': [0.5540973523936195, 0.15165276355285293, 0.22199053588004086]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: f07a678caf5b8ea43212ad5a337315ad102b1ae725b01cf669f7af9bd0eea2ea

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
| `object` | offset from object initial position (0.5136961687321454, -0.02302132862361297, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5540973523936195, 0.15165276355285293, 0.22199053588004086) | final destination targets |
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

## Current Skill (Q=-0.037) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_grasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.08
  weight: 0.2
- id: lift_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.25
  weight: 0.3
- id: place_goal
  target_entity: object
  weight: 0.5
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
    - 0.08
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.06
      - 0.15
      default: 0.08
      binds_to:
      - path: target.offset.z
        mode: replace
    generator.speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_grasp
- id: descend_grasp
  type: descend
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
    - 0.01
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    grasp_z:
      type: scalar
      range:
      - 0.0
      - 0.04
      default: 0.01
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_grasp
- id: grasp_object
  type: grasp
  control: position_control
  termination: grasp_success
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  parameters:
    grasp_offset:
      type: scalar
      range:
      - -0.03
      - 0.0
      default: -0.01
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_grasp
- id: lift_object
  type: lift
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
    - 0.25
    tolerance: 0.03
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.15
      - 0.35
      default: 0.25
      binds_to:
      - path: target.offset.z
        mode: replace
  guards:
  - id: lift_check
    when: after_phase
    predicate: object_lifted
    threshold: 0.02
    on_failure: retry
  - id: grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.02
  subtask_id: lift_object
- id: transport_to_goal
  type: approach
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.05
    tolerance: 0.03
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_goal
- id: descend_to_place
  type: descend
  generator: linear_cartesian
  control: impedance_control
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
    descend_speed:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
    place_height_adjust:
      type: scalar
      range:
      - -0.05
      - 0.05
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: place_goal
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
  parameters:
    release_time:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: duration.max_time
        mode: replace
- id: retract_from_place
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.03
    orientation:
      mode: keep_current
  parameters:
    retract_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.08], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - generator.speed: status=consumed; consumers=generator.speed (replace)
- **descend_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.01], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - grasp_z: status=consumed; consumers=target.offset.z (replace)
- **grasp_object** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - grasp_offset: status=consumed; consumers=target.offset.z (replace)
- **lift_object** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.25], tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
  - guards:
    - id=lift_check, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.02
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.0
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.02]
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.05], tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - place_height_adjust: status=consumed; consumers=target.offset.z (replace)
- **release_object** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - release_time: status=consumed; consumers=duration.max_time (replace)
- **retract_from_place** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.037
- **task_score** (E): 0.328
- **fitness_score**: 0.643  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.680

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_object | 1.00 | 0.1387 |
| descend_grasp | 1.00 | 0.1303 |
| grasp_object | 1.00 | 0.0118 |
| lift_object | 1.00 | 0.1304 |
| transport_to_goal | 1.00 | 0.2004 |
| descend_to_place | 1.00 | 0.0433 |
| release_object | 1.00 | 0.0211 |
| retract_from_place | 1.00 | 0.1083 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.495, 0.001, 0.165) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 |
| descend_grasp | descend | 1.00 / step_budget | (0.495, 0.001, 0.165)→(0.492, 0.001, 0.035) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 |
| grasp_object | grasp | 1.00 / step_budget | (0.492, 0.001, 0.035)→(0.484, 0.000, 0.027) | (0.497, 0.001, 0.026)→(0.497, 0.000, 0.026) | 0.265→0.266 |
| lift_object | lift | 1.00 / step_budget | (0.484, 0.000, 0.027)→(0.492, 0.000, 0.157) | (0.497, 0.000, 0.026)→(0.512, 0.001, 0.152) | 0.266→0.210 |
| transport_to_goal | approach | 1.00 / step_budget | (0.492, 0.000, 0.157)→(0.571, 0.164, 0.220) | (0.512, 0.001, 0.152)→(0.587, 0.164, 0.205) | 0.210→0.029 |
| descend_to_place | descend | 1.00 / step_budget | (0.571, 0.164, 0.220)→(0.576, 0.176, 0.179) | (0.587, 0.164, 0.205)→(0.590, 0.176, 0.158) | 0.029→0.033 |
| release_object | release | 1.00 / step_budget | (0.576, 0.176, 0.179)→(0.570, 0.174, 0.199) | (0.590, 0.176, 0.158)→(0.575, 0.182, 0.012) | 0.033→0.175 |
| retract_from_place | retract | 1.00 / step_budget | (0.570, 0.174, 0.199)→(0.580, 0.183, 0.307) | (0.575, 0.182, 0.012)→(0.575, 0.183, 0.016) | 0.175→0.171 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.418
- phase_score: 0.451
- phase_breakdown.lift_object_score: 0.098
- phase_breakdown.place_goal_score: 0.770
- phase_breakdown.reach_grasp_score: 0.183
- grasp_place_fitness: 0.688

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.688
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.418
- **Median Q (composite search score)**: -0.043
- **K-run variance**: 0.0012
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.378


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `096c354712624ed6bd8f9b9cbbbc2b7d35a94d9c1517cfb8353e2e383be5aaf0`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `3798aa6551d21849355469c7d63897f628ac7de9267c18bb4301fe6cfaae0164`; realized-scene SHA-256: `f07a678caf5b8ea43212ad5a337315ad102b1ae725b01cf669f7af9bd0eea2ea`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5137,-0.02302,0.03]},{"name":"goal","value":[0.5541,0.15165,0.22199]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5137,-0.02302,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5541,0.15165,0.22199]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.5198,"average_solve_count":202.0,"average_success_count":202.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.12213,"approach_object.generator.speed":0.1525,"descend_grasp.grasp_z":0.00108,"descend_to_place.descend_speed":0.03772,"descend_to_place.place_height_adjust":-0.00411,"grasp_object.grasp_offset":-0.02326,"lift_object.lift_height":0.15055,"release_object.release_time":0.48882,"retract_from_place.retract_speed":0.15436,"transport_to_goal.transport_speed":0.05818},"optimized_scores":{"best_composite_score":-0.07489,"best_fitness_score":0.60511,"best_task_score":0.25273},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":129.0,"contact_point_centroid":[0.54431,0.1568,-0.00936],"force_p95":1.59,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.85522,"mean_force":0.58845,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.54375,0.13929,0.24971]},{"body_a":"world","body_b":"grasp_target","contact_count":65.0,"contact_point_centroid":[0.51149,-0.02213,-0.00149],"force_p95":0.59932,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63729,"mean_force":0.18389,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49915,-0.02231,0.02757]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3561.0,"contact_point_centroid":[0.50448,-0.00324,0.08099],"force_p95":0.11268,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30927,"mean_force":0.07355,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50191,-0.02222,0.07843]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3944.0,"contact_point_centroid":[0.50449,-0.04107,0.07889],"force_p95":0.10872,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29311,"mean_force":0.0682,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50182,-0.02222,0.0772]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":618.0,"contact_point_centroid":[0.55112,0.1221,0.22538],"force_p95":0.20217,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28211,"mean_force":0.10602,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.54665,0.14027,0.22892]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":675.0,"contact_point_centroid":[0.55057,0.15876,0.22483],"force_p95":0.19517,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27755,"mean_force":0.10558,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.54647,0.14021,0.22861]},{"body_a":"world","body_b":"grasp_target","contact_count":740.0,"contact_point_centroid":[0.54335,0.15677,-0.00227],"force_p95":0.13432,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24562,"mean_force":0.11614,"phase_index":7.0,"phase_name":"retract_from_place","phase_type":"retract","tcp_position_centroid":[0.54666,0.1439,0.29737]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":498.0,"contact_point_centroid":[0.55287,0.11733,0.2428],"force_p95":0.17389,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21865,"mean_force":0.09593,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.54755,0.13563,0.24435]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":427.0,"contact_point_centroid":[0.5529,0.15393,0.2437],"force_p95":0.19342,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2163,"mean_force":0.11034,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.5475,0.13544,0.24479]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5137,-0.0228,-0.00206],"force_p95":0.14078,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.193,"mean_force":0.12764,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50148,-0.02237,0.02776]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4797.0,"contact_point_centroid":[0.5314,0.0364,0.19863],"force_p95":0.11152,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16985,"mean_force":0.08157,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52619,0.05486,0.19742]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4177.0,"contact_point_centroid":[0.5321,0.07595,0.20079],"force_p95":0.11835,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14716,"mean_force":0.08985,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52687,0.0573,0.19919]},{"body_a":"world","body_b":"grasp_target","contact_count":944.0,"contact_point_centroid":[0.5137,-0.02302,-0.00186],"force_p95":0.13706,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12314,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50356,-0.00916,0.2368]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4089.0,"contact_point_centroid":[0.50092,-0.00315,0.02925],"force_p95":0.07783,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12496,"mean_force":0.05181,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50028,-0.02235,0.02649]},{"body_a":"world","body_b":"grasp_target","contact_count":1676.0,"contact_point_centroid":[0.5137,-0.02302,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.50711,-0.02079,0.10209]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4924.0,"contact_point_centroid":[0.50094,-0.04145,0.02832],"force_p95":0.06979,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08908,"mean_force":0.04479,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50029,-0.02235,0.02649]}],"total_contact_groups":16},"final_pose_error":0.02955,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.54332,0.15668,0.01602],"final_tcp_position":[0.55096,0.14887,0.34274],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"phases":[{"n_steps":237.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_grasp","tcp_end":[0.5084,-0.01912,0.17089],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14502,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":419.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_grasp","tcp_end":[0.50859,-0.02253,0.03549],"tcp_start":[0.5084,-0.01912,0.17089],"tcp_to_object_dist_end":0.01077,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51356,-0.02225,0.02579],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26529,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"reach_grasp","tcp_end":[0.50025,-0.02234,0.02645],"tcp_start":[0.50859,-0.02253,0.03549],"tcp_to_object_dist_end":0.01333,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":246.0,"n_steps_budget":960.0,"object_pos_end":[0.52874,-0.02203,0.14291],"object_pos_start":[0.51356,-0.02225,0.02579],"object_to_goal_dist_end":0.19251,"object_to_goal_dist_start":0.26529,"object_z_max":0.14246,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_object","tcp_end":[0.5081,-0.02216,0.1472],"tcp_start":[0.50025,-0.02234,0.02645],"tcp_to_object_dist_end":0.02108,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":384.0,"n_steps_budget":1000.0,"object_pos_end":[0.56275,0.13153,0.23738],"object_pos_start":[0.52874,-0.02203,0.14291],"object_to_goal_dist_end":0.02677,"object_to_goal_dist_start":0.19251,"object_z_max":0.23713,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_goal","tcp_end":[0.54671,0.13174,0.25124],"tcp_start":[0.5081,-0.02216,0.1472],"tcp_to_object_dist_end":0.0212,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":48.0,"n_steps_budget":1000.0,"object_pos_end":[0.56561,0.14066,0.21711],"object_pos_start":[0.56275,0.13153,0.23738],"object_to_goal_dist_end":0.01665,"object_to_goal_dist_start":0.02677,"object_z_max":0.23762,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_goal","tcp_end":[0.54862,0.14037,0.2332],"tcp_start":[0.54671,0.13174,0.25124],"tcp_to_object_dist_end":0.02339,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54182,0.15103,0.00318],"object_pos_start":[0.56561,0.14066,0.21711],"object_to_goal_dist_end":0.21916,"object_to_goal_dist_start":0.01665,"object_z_max":0.21711,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.54372,0.13929,0.25482],"tcp_start":[0.54862,0.14037,0.2332],"tcp_to_object_dist_end":0.25192,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":185.0,"n_steps_budget":600.0,"object_pos_end":[0.54332,0.15668,0.01602],"object_pos_start":[0.54182,0.15103,0.00318],"object_to_goal_dist_end":0.20631,"object_to_goal_dist_start":0.21916,"object_z_max":0.017,"phase_name":"retract_from_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.55096,0.14887,0.34274],"tcp_start":[0.54372,0.13929,0.25482],"tcp_to_object_dist_end":0.3269,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `ed2df336ade3d991e9495251c8398520a59dd014a70bd2d7bb71dc7aefccaa8a`; realized-scene SHA-256: `a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50118,0.04505,0.03]},{"name":"goal","value":[0.56442,0.24486,0.14677]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50118,0.04505,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.56442,0.24486,0.14677]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.78571,"average_solve_count":210.0,"average_success_count":210.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.09602,"approach_object.generator.speed":0.09217,"descend_grasp.grasp_z":0.0002,"descend_to_place.descend_speed":0.04769,"descend_to_place.place_height_adjust":-0.01484,"grasp_object.grasp_offset":-0.00378,"lift_object.lift_height":0.16796,"release_object.release_time":0.28793,"retract_from_place.retract_speed":0.11126,"transport_to_goal.transport_speed":0.07759},"optimized_scores":{"best_composite_score":0.00842,"best_fitness_score":0.68842,"best_task_score":0.41813},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":556.0,"contact_point_centroid":[0.56282,0.24224,-0.00346],"force_p95":0.68107,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.3551,"mean_force":0.19461,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.55161,0.23158,0.14923]},{"body_a":"world","body_b":"grasp_target","contact_count":66.0,"contact_point_centroid":[0.49884,0.04266,-0.00163],"force_p95":0.63147,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65861,"mean_force":0.19856,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48703,0.04302,0.02733]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":77.0,"contact_point_centroid":[0.56046,0.24926,0.13913],"force_p95":0.32437,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.42749,"mean_force":0.11805,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.55656,0.23393,0.14486]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":664.0,"contact_point_centroid":[0.55963,0.24396,0.16373],"force_p95":0.20907,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.42335,"mean_force":0.13814,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.55499,0.22611,0.16801]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":523.0,"contact_point_centroid":[0.55955,0.20753,0.16619],"force_p95":0.22887,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35234,"mean_force":0.15296,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.55481,0.22547,0.16985]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4468.0,"contact_point_centroid":[0.49213,0.06174,0.0853],"force_p95":0.1105,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31372,"mean_force":0.06791,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4897,0.04283,0.08339]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4079.0,"contact_point_centroid":[0.49241,0.02387,0.08826],"force_p95":0.11332,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3046,"mean_force":0.07218,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48988,0.04283,0.08573]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2.0,"contact_point_centroid":[0.56483,0.21899,0.13959],"force_p95":0.29332,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29653,"mean_force":0.26448,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.5574,0.23384,0.14668]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50125,0.04463,-0.00217],"force_p95":0.17435,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2624,"mean_force":0.13629,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48936,0.04326,0.02735]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3846.0,"contact_point_centroid":[0.52761,0.10596,0.17348],"force_p95":0.12172,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2307,"mean_force":0.09109,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52179,0.12447,0.17232]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3716.0,"contact_point_centroid":[0.52881,0.1469,0.17396],"force_p95":0.12093,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21903,"mean_force":0.09283,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52306,0.12833,0.17283]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3752.0,"contact_point_centroid":[0.48929,0.02397,0.02917],"force_p95":0.08628,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15047,"mean_force":0.05562,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48819,0.04316,0.02613]},{"body_a":"world","body_b":"grasp_target","contact_count":1228.0,"contact_point_centroid":[0.50118,0.04505,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12302,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49839,0.01859,0.2235]},{"body_a":"world","body_b":"grasp_target","contact_count":888.0,"contact_point_centroid":[0.56271,0.24217,-0.00199],"force_p95":0.12283,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12335,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_from_place","phase_type":"retract","tcp_position_centroid":[0.55466,0.23603,0.21592]},{"body_a":"world","body_b":"grasp_target","contact_count":1376.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.49575,0.04113,0.08869]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4956.0,"contact_point_centroid":[0.48883,0.06232,0.02798],"force_p95":0.07648,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08857,"mean_force":0.04551,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.4882,0.04316,0.02614]}],"total_contact_groups":16},"final_pose_error":0.02973,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.56271,0.24217,0.01602],"final_tcp_position":[0.5602,0.24155,0.26754],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"phases":[{"n_steps":308.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_grasp","tcp_end":[0.49791,0.03861,0.14437],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11857,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":344.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_grasp","tcp_end":[0.49631,0.04388,0.03474],"tcp_start":[0.49791,0.03861,0.14437],"tcp_to_object_dist_end":0.01006,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50108,0.04318,0.02543],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24374,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"reach_grasp","tcp_end":[0.48817,0.04315,0.0261],"tcp_start":[0.49631,0.04388,0.03474],"tcp_to_object_dist_end":0.01293,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":276.0,"n_steps_budget":1000.0,"object_pos_end":[0.51708,0.04309,0.15914],"object_pos_start":[0.50108,0.04318,0.02543],"object_to_goal_dist_end":0.20762,"object_to_goal_dist_start":0.24374,"object_z_max":0.15868,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_object","tcp_end":[0.49609,0.04284,0.16392],"tcp_start":[0.48817,0.04315,0.0261],"tcp_to_object_dist_end":0.02153,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":346.0,"n_steps_budget":1000.0,"object_pos_end":[0.56992,0.21916,0.1702],"object_pos_start":[0.51708,0.04309,0.15914],"object_to_goal_dist_end":0.03521,"object_to_goal_dist_start":0.20762,"object_z_max":0.17019,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_goal","tcp_end":[0.55352,0.2193,0.18552],"tcp_start":[0.49609,0.04284,0.16392],"tcp_to_object_dist_end":0.02244,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":88.0,"n_steps_budget":1000.0,"object_pos_end":[0.57079,0.23474,0.12295],"object_pos_start":[0.56992,0.21916,0.1702],"object_to_goal_dist_end":0.02666,"object_to_goal_dist_start":0.03521,"object_z_max":0.1702,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_goal","tcp_end":[0.5574,0.23384,0.14668],"tcp_start":[0.55352,0.2193,0.18552],"tcp_to_object_dist_end":0.02726,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56271,0.24215,0.016],"object_pos_start":[0.57079,0.23474,0.12295],"object_to_goal_dist_end":0.13081,"object_to_goal_dist_start":0.02666,"object_z_max":0.12295,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.55108,0.23133,0.16712],"tcp_start":[0.5574,0.23384,0.14668],"tcp_to_object_dist_end":0.15195,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":222.0,"n_steps_budget":750.0,"object_pos_end":[0.56271,0.24217,0.01602],"object_pos_start":[0.56271,0.24215,0.016],"object_to_goal_dist_end":0.13079,"object_to_goal_dist_start":0.13081,"object_z_max":0.01602,"phase_name":"retract_from_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.5602,0.24155,0.26754],"tcp_start":[0.55108,0.23133,0.16712],"tcp_to_object_dist_end":0.25153,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `291bc6f2bd023fc25503740a7343328e565e43fc71fa3c9c5d2fdbe2d4351fd2`; realized-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47616,-0.02015,0.03]},{"name":"goal","value":[0.63142,0.15919,0.19002]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.47616,-0.02015,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63142,0.15919,0.19002]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.68398,"average_solve_count":231.0,"average_success_count":231.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.13135,"approach_object.generator.speed":0.17846,"descend_grasp.grasp_z":2e-05,"descend_to_place.descend_speed":0.05256,"descend_to_place.place_height_adjust":-0.04909,"grasp_object.grasp_offset":-0.01529,"lift_object.lift_height":0.16289,"release_object.release_time":0.44662,"retract_from_place.retract_speed":0.1083,"transport_to_goal.transport_speed":0.06585},"optimized_scores":{"best_composite_score":-0.04307,"best_fitness_score":0.63693,"best_task_score":0.31242},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":475.0,"contact_point_centroid":[0.62063,0.1503,-0.00382],"force_p95":1.0194,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.32764,"mean_force":0.22952,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61665,0.15143,0.15999]},{"body_a":"world","body_b":"grasp_target","contact_count":63.0,"contact_point_centroid":[0.47382,-0.0195,-0.00147],"force_p95":0.61548,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63431,"mean_force":0.20419,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46296,-0.01952,0.02845]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":108.0,"contact_point_centroid":[0.62592,0.13674,0.14938],"force_p95":0.26867,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.42674,"mean_force":0.12118,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.6219,0.15301,0.15499]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1088.0,"contact_point_centroid":[0.62186,0.12876,0.18864],"force_p95":0.17653,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31106,"mean_force":0.11694,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61754,0.14684,0.19307]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1085.0,"contact_point_centroid":[0.62155,0.16483,0.18941],"force_p95":0.18774,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29122,"mean_force":0.1193,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61742,0.14669,0.19397]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4113.0,"contact_point_centroid":[0.46734,-0.00043,0.08664],"force_p95":0.10939,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28761,"mean_force":0.06751,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46552,-0.01948,0.08409]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4480.0,"contact_point_centroid":[0.46736,-0.03845,0.08515],"force_p95":0.105,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28348,"mean_force":0.06315,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46546,-0.01948,0.08333]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":25.0,"contact_point_centroid":[0.62922,0.17061,0.14982],"force_p95":0.23571,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24616,"mean_force":0.17863,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62264,0.15308,0.15663]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5042.0,"contact_point_centroid":[0.54396,0.03893,0.18947],"force_p95":0.128,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22746,"mean_force":0.08967,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53836,0.05736,0.18881]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4606.0,"contact_point_centroid":[0.54765,0.08009,0.19134],"force_p95":0.12972,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2102,"mean_force":0.09477,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5421,0.06156,0.19056]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.02002,-0.00205],"force_p95":0.13844,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18945,"mean_force":0.12699,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46523,-0.01958,0.02842]},{"body_a":"world","body_b":"grasp_target","contact_count":868.0,"contact_point_centroid":[0.47616,-0.02015,-0.00185],"force_p95":0.13721,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12319,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48887,-0.00786,0.24201]},{"body_a":"world","body_b":"grasp_target","contact_count":1220.0,"contact_point_centroid":[0.62038,0.15162,-0.00199],"force_p95":0.12326,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12393,"mean_force":0.12266,"phase_index":7.0,"phase_name":"retract_from_place","phase_type":"retract","tcp_position_centroid":[0.62094,0.15415,0.24175]},{"body_a":"world","body_b":"grasp_target","contact_count":1840.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.47347,-0.01807,0.10699]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5062.0,"contact_point_centroid":[0.4638,-0.00033,0.02989],"force_p95":0.06598,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09505,"mean_force":0.04287,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46411,-0.01955,0.02732]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5162.0,"contact_point_centroid":[0.46403,-0.03881,0.0293],"force_p95":0.06672,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.083,"mean_force":0.04304,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46412,-0.01955,0.02733]}],"total_contact_groups":16},"final_pose_error":0.02984,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.62038,0.15162,0.01602],"final_tcp_position":[0.62797,0.15761,0.31041],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"phases":[{"n_steps":218.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_grasp","tcp_end":[0.47761,-0.01651,0.18072],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15475,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":460.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_grasp","tcp_end":[0.47196,-0.01972,0.0351],"tcp_start":[0.47761,-0.01651,0.18072],"tcp_to_object_dist_end":0.01001,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47603,-0.0196,0.0258],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28823,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"reach_grasp","tcp_end":[0.46409,-0.01955,0.02729],"tcp_start":[0.47196,-0.01972,0.0351],"tcp_to_object_dist_end":0.01204,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":259.0,"n_steps_budget":1000.0,"object_pos_end":[0.49115,-0.01946,0.15476],"object_pos_start":[0.47603,-0.0196,0.0258],"object_to_goal_dist_end":0.22987,"object_to_goal_dist_start":0.28823,"object_z_max":0.15429,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_object","tcp_end":[0.47123,-0.01949,0.15933],"tcp_start":[0.46409,-0.01955,0.02729],"tcp_to_object_dist_end":0.02043,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":443.0,"n_steps_budget":1000.0,"object_pos_end":[0.62752,0.1413,0.20612],"object_pos_start":[0.49115,-0.01946,0.15476],"object_to_goal_dist_end":0.02439,"object_to_goal_dist_start":0.22987,"object_z_max":0.20602,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_goal","tcp_end":[0.6138,0.14137,0.22419],"tcp_start":[0.47123,-0.01949,0.15933],"tcp_to_object_dist_end":0.02269,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":132.0,"n_steps_budget":1000.0,"object_pos_end":[0.63352,0.15278,0.13404],"object_pos_start":[0.62752,0.1413,0.20612],"object_to_goal_dist_end":0.05638,"object_to_goal_dist_start":0.02439,"object_z_max":0.20617,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_goal","tcp_end":[0.62291,0.15302,0.15762],"tcp_start":[0.6138,0.14137,0.22419],"tcp_to_object_dist_end":0.02586,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62036,0.15174,0.01601],"object_pos_start":[0.63352,0.15278,0.13404],"object_to_goal_dist_end":0.17452,"object_to_goal_dist_start":0.05638,"object_z_max":0.13404,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.6163,0.15133,0.1761],"tcp_start":[0.62291,0.15302,0.15762],"tcp_to_object_dist_end":0.16015,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":305.0,"n_steps_budget":960.0,"object_pos_end":[0.62038,0.15162,0.01602],"object_pos_start":[0.62036,0.15174,0.01601],"object_to_goal_dist_end":0.17451,"object_to_goal_dist_start":0.17452,"object_z_max":0.01602,"phase_name":"retract_from_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.62797,0.15761,0.31041],"tcp_start":[0.6163,0.15133,0.1761],"tcp_to_object_dist_end":0.29455,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```